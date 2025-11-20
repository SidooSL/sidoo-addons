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

    def _process_logical_record(
        self, odoo_vals, external_id_name, record_id, write=False
    ):
        """Processes a single logical record in an isolated job."""
        record = self.env["ai.record"].browse(record_id)
        try:
            if write:
                self.write_odoo_record(record, odoo_vals)
            else:
                self.create_odoo_record(record, odoo_vals, external_id_name)
        except Exception as e:
            error_traceback = traceback.format_exc()
            _logger.error(
                f"Error al procesar el registro lógico para el registro {record.id}: {str(e)}\n{error_traceback}"
            )
            # Associate error with the batch and the specific record
            self.env["ai.error"].create(
                {
                    "name": str(e),
                    "stacktrace": error_traceback,
                    "record_id": record.id,
                    "batch_id": record.batch_id.id,
                }
            )

    def process_batch(self, record_sublist=False):  # noqa
        """
        Groups records from a batch into logical records (especially for to-many relations)
        and queues a separate job for each logical record.
        """
        if record_sublist:
            records = sorted(record_sublist, key=lambda x: x.sequence)
        else:
            records = self.env["ai.record"].search(
                [("batch_id", "=", self.id), ("header", "=", False)], order="sequence"
            )
        if not records:
            return

        first_record = records[0]
        if first_record.file_id.skip:
            return

        has_tomany = self.env["ai.template.file.map"].has_tomany(first_record)
        if not has_tomany:
            # Simple case: one job per record
            for record in records:
                self._queue_single_record_job(record)
            return

        # Complex case: group records with to-many fields
        model = first_record.file_id.template_id.mapper_id.model_id.model
        group_head_record = None
        group_external_id = None
        group_vals = {}

        with_errors = False
        for record in records:
            if record.header:
                continue

            try:
                current_external_id = self.env[
                    "ai.template.file.map"
                ].normalize_external_id(model, record.col1 or "", record)

                # If a new master record starts (and it's not the very first one)
                if (
                    group_external_id
                    and record.col1
                    and group_external_id != current_external_id
                ):
                    # Queue the completed group for processing
                    self._queue_logical_record_job(
                        group_vals, group_external_id, group_head_record.id
                    )
                    # Reset for the new group
                    group_vals = {}

                # If this is the first line of a new group
                if not group_vals:
                    group_head_record = record
                    group_external_id = current_external_id
                    group_vals = self.env["ai.template.file.map"].process_record(
                        record
                    )
                    if not group_vals:
                        continue  # Record was invalid, skip to next. Error logged in process_record

                    # Add first to-many line
                    to_many_vals = self.env["ai.template.file.map"].map_tomany(record)
                    group_vals.update(to_many_vals)
                else:  # Append to-many lines to the existing group
                    to_many_vals = self.env["ai.template.file.map"].map_tomany(record)
                    for key, val in to_many_vals.items():
                        if key in group_vals:
                            group_vals[key].extend(val)
                        else:
                            group_vals[key] = val
            except Exception as e:
                # Log errors during the grouping/preparation phase
                error_traceback = traceback.format_exc()
                with_errors = True
                _logger.error(
                    f"Error preparing job for record {record.id}: {str(e)}\n{error_traceback}"
                )
                self.env["ai.error"].create(
                    {
                        "name": str(e),
                        "stacktrace": error_traceback,
                        "record_id": record.id,
                        "batch_id": self.id,
                    }
                )

        # Queue the last group of records
        if not with_errors and group_vals:
            self._queue_logical_record_job(
                group_vals, group_external_id, group_head_record.id
            )

    def _queue_logical_record_job(self, odoo_vals, external_id_name, record_id):
        """Helper to check for existing record and queue the processing job."""
        record = self.env["ai.record"].browse(record_id)
        try:
            # Check if record exists to decide between write or create
            record_exists = bool(
                external_id_name
                and self.env.ref(external_id_name, raise_if_not_found=False)
            )
            self.with_delay()._process_logical_record(
                odoo_vals, external_id_name, record_id, write=record_exists
            )
        except Exception as e:
            error_traceback = traceback.format_exc()
            _logger.error(
                f"Error queuing job for record {record.id}: {str(e)}\n{error_traceback}"
            )
            self.env["ai.error"].create(
                {
                    "name": str(e),
                    "stacktrace": error_traceback,
                    "record_id": record.id,
                    "batch_id": self.id,
                }
            )

    def _queue_single_record_job(self, record):
        """Helper to prepare and queue a job for a single non-to-many record."""
        try:
            odoo_vals = self.env["ai.template.file.map"].process_record(record)
            if not odoo_vals:
                return  # Error already logged by process_record

            model = record.file_id.template_id.mapper_id.model_id.model
            external_id_name = self.env["ai.template.file.map"].normalize_external_id(
                model, record.col1 or "", record
            )

            self._queue_logical_record_job(odoo_vals, external_id_name, record.id)
        except Exception as e:
            error_traceback = traceback.format_exc()
            _logger.error(
                f"Error preparing job for single record {record.id}: {str(e)}\n{error_traceback}"
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
                f"No se permite la modificación del registro {record.id} del batch {self.id} de la plantilla {self.file_id.template_id.name} con id externo {record.col1}. Suele ocurrir cuando no has indicado ni id de cabecera ni de línea."
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
