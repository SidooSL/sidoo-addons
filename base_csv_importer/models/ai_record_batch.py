import logging
import traceback

from odoo import fields, models

_logger = logging.getLogger(__name__)


class AIRecordBatch(models.Model):
    _name = "ai.record.batch"
    _description = "Lote de Registros por job"

    file_id = fields.Many2one(
        "ai.file", string="Fichero", required=True, ondelete="cascade"
    )
    bundle_id = fields.Many2one(
        "ai.file.bundle", string="Histórico", related="file_id.bundle_id", store=True
    )
    record_ids = fields.One2many("ai.record", "batch_id", string="Registros")
    job_id = fields.Many2one("queue.job", string="Job")
    job_state = fields.Selection(string="Estado del Job", related="job_id.state")
    error_ids = fields.One2many("ai.error", "batch_id", string="Errores")

    def process_batch(self, record_sublist=False):  # noqa
        if record_sublist:
            records = sorted(record_sublist, key=lambda x: x.sequence)
        else:
            records = self.env["ai.record"].search(
                [("batch_id", "=", self.id), ("header", "=", False)], order="sequence"
            )
        if not records:
            return
        record = records[0] if not records[0].header else records[1]
        if record.file_id.skip:
            return
        has_tomany = False
        if records:
            has_tomany = self.env["ai.template.file.map"].has_tomany(record)

        external_id = False
        model = record.mapped("file_id.template_id.mapper_id.model_id.model")[0]
        value = record.col1 or ""
        previous_external_id = self.env["ai.template.file.map"].normalize_external_id(
            model, value, record
        )
        has_tomanay_loaded = False
        odoo_vals = {}
        for record in records:
            if record.header:
                continue
            _logger.info(
                f"Processing record {record.id} of batch {self.id} from template {self.file_id.template_id.name}"
            )
            external_id_name = record.col1 or ""
            try:
                external_id_name = self.env[
                    "ai.template.file.map"
                ].normalize_external_id(
                    record.mapped("file_id.template_id.mapper_id.model_id.model")[0],
                    external_id_name,
                    record,
                )
                external_id = (
                    self.env.ref(external_id_name, raise_if_not_found=False)
                    if external_id_name
                    else False
                )
                if (
                    has_tomany
                    and previous_external_id != external_id_name
                    and record.col1
                ):
                    external_id = self.env.ref(
                        previous_external_id, raise_if_not_found=False
                    )
                    if external_id:
                        self.write_odoo_record(record, odoo_vals)
                    else:
                        self.create_odoo_record(record, odoo_vals, previous_external_id)
                    previous_external_id = external_id_name
                    odoo_vals = self.env["ai.template.file.map"].process_record(record)
                    to_many_values = self.env["ai.template.file.map"].map_tomany(record)
                    to_many_keys = to_many_values.keys()
                    for key in to_many_keys:
                        if key in odoo_vals:
                            odoo_vals[key].append(to_many_values[key][0])
                        else:
                            odoo_vals.update(to_many_values)
                    has_tomanay_loaded = True
                elif has_tomany:
                    if not has_tomanay_loaded:
                        odoo_vals = self.env["ai.template.file.map"].process_record(
                            record
                        )
                        if not odoo_vals:
                            # Error ya registrado, pasamos al siguiente registro
                            continue
                    to_many_values = self.env["ai.template.file.map"].map_tomany(record)
                    to_many_keys = to_many_values.keys()
                    for key in to_many_keys:
                        if key in odoo_vals:
                            odoo_vals[key].append(to_many_values[key][0])
                        else:
                            odoo_vals.update(to_many_values)
                    has_tomanay_loaded = True
                else:
                    self.env["ai.template.file.map"].process_record(record)
            except Exception as e:
                error_traceback = traceback.format_exc()
                _logger.error(
                    f"Error al procesar el registro {record.id}: {str(e)}\n{error_traceback}"
                )

                self.env["ai.error"].create(
                    {
                        "name": str(e),
                        "stacktrace": error_traceback,
                        "record_id": record.id,
                        "batch_id": self.id,
                    }
                )
        external_id = self.env.ref(external_id_name, raise_if_not_found=False)
        if not external_id and odoo_vals and previous_external_id:
            try:
                self.create_odoo_record(record, odoo_vals, previous_external_id)
            except Exception as e:
                error_traceback = traceback.format_exc()
                _logger.error(
                    f"Error al procesar el registro {record.id}: {str(e)}\n{error_traceback}"
                )

                self.env["ai.error"].create(
                    {
                        "name": str(e),
                        "stacktrace": error_traceback,
                        "record_id": record.id,
                        "batch_id": self.id,
                    }
                )

    def queue_batch(self):
        for batch in self:
            job = self.with_delay().process_batch()
            batch.job_id = (
                self.env["queue.job"].search([("uuid", "=", job.uuid)], limit=1).id
            )

    def create_odoo_record(self, record, odoo_vals, external_id_name):
        tomany_keys = self.env["ai.template.file.map"].tomany_keys(record)
        if not tomany_keys:
            odoo_id = self.env[
                self.env["ai.template.file.map"].get_destination_model(record)
            ].create(odoo_vals)
        else:
            main_model_data = odoo_vals.copy()
            for key in tomany_keys:
                if key in main_model_data.keys():
                    main_model_data.pop(key)
                else:
                    raise ValueError(
                        f"El modelo principal tiene relación con {key} pero no se ha encontrado en el registro. Solucione los errores en registros anteriores."
                    )
            odoo_id = (
                self.env[self.env["ai.template.file.map"].get_destination_model(record)]
                .with_context(check_move_validity=False)
                .create(main_model_data)
            )
            for key in tomany_keys:
                values = odoo_vals.pop(key)
                mapper = record.mapped("file_id.template_id.mapper_id")
                related_field = self.env["ir.model.fields"].search(
                    [
                        ("model", "=", mapper.model_id.model),
                        ("name", "=", key.split("/")[0]),
                    ],
                    limit=1,
                )
                for value in values:
                    if "id" in value.keys():
                        value["id"] = str(value.get("id", "")) or record.col1
                    related_external_id_name = value.get("id", "") or record.col1
                    if (
                        not related_external_id_name
                        or "." not in related_external_id_name
                    ):
                        related_external_id_name = self.env[
                            "ai.template.file.map"
                        ].normalize_external_id(
                            related_field.relation,
                            value.get("id", None) or record.col1,
                            record,
                        )
                    existing_related_odoo_id = False
                    if related_external_id_name:
                        existing_related_odoo_id = self.env.ref(
                            related_external_id_name, raise_if_not_found=False
                        )
                    if existing_related_odoo_id:
                        existing_related_odoo_id.with_context(
                            check_move_validity=False
                        ).write(value)
                    else:
                        value[related_field.relation_field] = odoo_id.id
                        related_odoo_id = (
                            self.env[related_field.relation]
                            .with_context(check_move_validity=False)
                            .create(value)
                        )
                        existing_external_id = self.env.ref(
                            related_external_id_name, raise_if_not_found=False
                        )
                        if not existing_external_id:
                            self.env["ir.model.data"].create(
                                {
                                    "name": related_external_id_name.split(".")[1],
                                    "module": related_external_id_name.split(".")[0],
                                    "model": related_field.relation,
                                    "res_id": related_odoo_id.id,
                                }
                            )
        existing_external_id = self.env.ref(external_id_name, raise_if_not_found=False)
        external_id = False
        if not existing_external_id:
            external_id = self.env["ir.model.data"].create(
                {
                    "name": external_id_name.split(".")[1],
                    "module": external_id_name.split(".")[0],
                    "model": self.env["ai.template.file.map"].get_destination_model(
                        record
                    ),
                    "res_id": odoo_id.id,
                }
            )
        if not external_id and existing_external_id:
            external_id = self.env["ai.template.file.map"].get_ir_model_data(
                existing_external_id
            )
        record.external_id = external_id
        self.execute_actions(odoo_id, record, odoo_vals)
        return odoo_id

    def execute_actions(self, odoo_id, record, odoo_vals):
        for action in record.file_id.template_id.mapper_id.action_ids.sorted(
            "sequence"
        ):
            try:
                method = getattr(
                    odoo_id.with_context(importer_record=record, odoo_vals=odoo_vals),
                    action.action,
                )
                method()
            except Exception as e:
                error_traceback = traceback.format_exc()
                _logger.error(
                    f"Error al ejecutar la acción {action.action} en el registro {record.id}: {str(e)}\n{error_traceback}"
                )
                self.env["ai.error"].create(
                    {
                        "name": str(e),
                        "stacktrace": error_traceback,
                        "record_id": record.id,
                        "batch_id": self.id,
                    }
                )

    def write_odoo_record(self, record, odoo_vals):
        model = record.mapped("file_id.template_id.mapper_id.model_id.model")[0]
        external_id_name = self.env["ai.template.file.map"].normalize_external_id(
            record.mapped("file_id.template_id.mapper_id.model_id.model")[0],
            odoo_vals["id"],
            record,
        )
        main_odoo_id = self.env.ref(external_id_name, raise_if_not_found=True)
        if model in ("account.move", "account.payment"):
            _logger.info(
                f"No se permite la modificación del registro {record.id} del batch {self.id} de la plantilla {self.file_id.template_id.name}"
            )
            return main_odoo_id
        tomany_keys = self.env["ai.template.file.map"].tomany_keys(record)
        if not tomany_keys:
            return (
                self.env[self.env["ai.template.file.map"].get_destination_model(record)]
                .with_context(check_move_validity=False)
                .write(odoo_vals)
            )
        for key in tomany_keys:
            if key in odoo_vals.keys():
                values = odoo_vals.pop(key)
            else:
                continue
            mapper = record.mapped("file_id.template_id.mapper_id")
            related_field = self.env["ir.model.fields"].search(
                [
                    ("model", "=", mapper.model_id.model),
                    ("name", "=", key.split("/")[0]),
                ],
                limit=1,
            )
            for value in values:
                external_id_name = self.env[
                    "ai.template.file.map"
                ].normalize_external_id(
                    related_field.relation, value.get("id", None) or record.col1, record
                )
                existing_related_odoo_id = self.env.ref(
                    external_id_name, raise_if_not_found=True
                )
                existing_related_odoo_id.write(value)
        self.execute_actions(main_odoo_id, record, odoo_vals)
        return main_odoo_id
