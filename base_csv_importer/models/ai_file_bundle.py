import base64
import csv
import io
import os
import re
import shutil
import zipfile
from io import TextIOWrapper

from odoo import _, fields, models
from odoo.exceptions import ValidationError

_COLS_TO_IMPORT = 50


class AIFileBundle(models.Model):
    _name = "ai.file.bundle"
    _description = "AI File Bundle"

    file_ids = fields.One2many("ai.file", "bundle_id", string="Ficheros")
    record_ids = fields.One2many("ai.record", "bundle_id", string="Registros")
    batch_ids = fields.One2many("ai.record.batch", "bundle_id", string="Lotes")

    def _compute_batch_ids(self):
        for record in self:
            record.batch_ids = record.mapped("file_ids.batch_ids")

    def _compute_record_count(self):
        for record in self:
            record.record_count = len(record.record_ids)

    record_count = fields.Integer(
        string="Cantidad de registros", compute="_compute_record_count"
    )
    job_record_count = fields.Integer(
        string="Cantidad de registros por job", default=100, required=True
    )
    name = fields.Char(string="Nombre", required=True)
    state = fields.Selection(
        [
            ("draft", "Borrador"),
            ("confirm", "Confirmado"),
            ("in_progress", "En Progreso"),
            ("done", "Finalizado"),
            ("done_error", "Finalizado con Errores"),
        ],
        string="Estado",
        default="draft",
    )
    type_id = fields.Many2one(
        "ai.import.type",
        string="Tipo de Importación",
        required=True,
        default=lambda self: self.env.ref("base_csv_importer.ai_import_type_basic"),
    )
    bundle_file = fields.Binary(
        string="Archivo",
    )
    bundle_file_name = fields.Char(string="Nombre del Archivo")
    error_ids = fields.One2many("ai.error", "bundle_id", string="Errores")

    def open_records(self):
        self.ensure_one()
        records = self.env["ai.record"].search([("bundle_id", "=", self.id)])

        action = self.env["ir.actions.act_window"]._for_xml_id(
            "base_csv_importer.action_base_csv_importer_records"
        )
        action.update(
            {
                "name": _("Registros para %s") % (self.name),
                "context": {
                    "search_default_has_errors": 1,
                    "search_default_group_by_file_id": 1,
                },
                "domain": [("id", "in", records.ids)],
            }
        )
        return action

    def import_bundle(self):
        for bundle in self:
            sanitized_name = re.sub(r"[^\w\-_\.]", "_", str(bundle.name))
            temp_dir = (
                "/tmp/" + self.env.cr.dbname + "/base_csv_importer/" + sanitized_name
            )

            bundle.validate_bundle(temp_dir)
            bundle.import_files(temp_dir)
            bundle.state = "confirm"

    def button_draft(self):
        for record in self:
            record.state = "draft"
            self.env["ai.error"].search([("bundle_id", "=", record.id)]).unlink()
            self.env["ai.record"].search([("bundle_id", "=", record.id)]).unlink()
            self.env["ai.record.batch"].search(
                [("file_id", "in", record.file_ids.ids)]
            ).unlink()
            self.env["ai.file"].search([("bundle_id", "=", record.id)]).unlink()

    def validate_bundle(self, temp_dir):
        if self.state != "draft":
            return

        if not self.bundle_file:
            raise ValidationError(_("No se ha proporcionado un archivo ZIP."))

        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir, exist_ok=True)

        zip_data = base64.b64decode(self.bundle_file)

        try:
            with zipfile.ZipFile(io.BytesIO(zip_data), "r") as zip_ref:
                zip_ref.extractall(temp_dir)
        except zipfile.BadZipFile as e:
            raise ValidationError(
                _("El archivo proporcionado no es un archivo ZIP válido.")
            ) from e

        valid_prefixes = [template.name for template in self.type_id.template_ids]

        for file_name in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, file_name)

            if not file_name.endswith(".csv"):
                raise ValidationError(
                    _("El archivo '%s' no tiene la extensión .csv.") % file_name
                )

            if not any(file_name.startswith(prefix) for prefix in valid_prefixes):
                raise ValidationError(
                    _("El archivo '%s' no coincide con ningún prefijo válido.")
                    % file_name
                )

            with open(file_path, "rb") as f:
                try:
                    wrapper = TextIOWrapper(f, encoding="utf-8")
                    reader = csv.reader(wrapper, delimiter=";")
                    next(reader)
                except UnicodeDecodeError as e:
                    raise ValidationError(
                        _("El archivo '%s' no está codificado en UTF-8.") % file_name
                    ) from e
                except csv.Error as e:
                    raise ValidationError(
                        _("El archivo '%s' no utiliza ';' como separador.") % file_name
                    ) from e

    def import_files(self, temp_dir):
        for bundle_record in self:
            for file_name in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, file_name)
                file_record = self.env["ai.file"].create(
                    {
                        "name": file_name,
                        "template_id": bundle_record.type_id.template_ids.filtered(
                            lambda t: file_name.startswith(t.name)  # noqa
                        ).id,
                        "bundle_id": bundle_record.id,
                    }
                )

                with open(file_path, "rb") as f:
                    wrapper = TextIOWrapper(f, encoding="utf-8")
                    reader = csv.reader(wrapper, delimiter=";")
                    headers = next(reader)

                    expected_columns = [
                        "bundle_id",
                        "file_id",
                        "header",
                        "sequence",
                    ] + [f"col{i}" for i in range(1, _COLS_TO_IMPORT)]
                    if len(headers) > len(expected_columns) - 1:
                        raise ValidationError(
                            _(
                                f"El archivo {file_name} contiene {len(headers)} columnas. El máximo está en {_COLS_TO_IMPORT}."
                            )
                        )
                    temp_data = io.StringIO()
                    writer = csv.writer(
                        temp_data,
                        delimiter="\t",
                        quoting=csv.QUOTE_NONE,
                        escapechar="\\",
                    )

                    padded_row = headers + [None] * (_COLS_TO_IMPORT - len(headers) - 1)
                    i = 0
                    writer.writerow(
                        [file_record.bundle_id.id, file_record.id, True, i] + padded_row
                    )
                    for row in reader:
                        i += 1
                        padded_row = row + [None] * (_COLS_TO_IMPORT - len(row) - 1)
                        writer.writerow(
                            [file_record.bundle_id.id, file_record.id, False, i]
                            + padded_row
                        )
                    temp_data.seek(0)

                    self._cr.copy_from(
                        temp_data,
                        "ai_record",
                        columns=expected_columns,
                    )

    def queue_files(
        self,
    ):
        for bundle in self:
            ordered_files = bundle.file_ids.filtered(lambda f: not f.skip).sorted(
                "sequence"
            )
            for file in ordered_files:
                file.queue_file()
            bundle.state = "in_progress"
            return True

    def check_status(
        self,
    ):
        records = self.search(
            [
                ("state", "not in", ("draft", "confirm")),
            ]
        )
        for bundle in records:
            all_jobs = bundle.mapped("file_ids.batch_ids.job_id")
            pending_job_ids = all_jobs.filtered(lambda b: b.state != "done")
            if pending_job_ids:
                states = pending_job_ids.mapped("state")
                if "failed" in states:
                    bundle.state = "done_error"
            if not pending_job_ids:
                if bundle.error_ids:
                    bundle.state = "done_error"
                else:
                    bundle.state = "done"
