from odoo import fields, models


class AIFile(models.Model):
    _name = "ai.file"
    _description = "AI File"

    bundle_id = fields.Many2one("ai.file.bundle", string="Histórico")
    name = fields.Char(string="Nombre del Fichero")
    queued = fields.Boolean(string="En cola", default=False)
    template_id = fields.Many2one("ai.template.file", string="Plantilla")
    sequence = fields.Integer(
        string="Secuencia", related="template_id.sequence", store=True
    )
    batch_ids = fields.One2many(
        "ai.record.batch", "file_id", string="Lotes de Registros"
    )
    error_ids = fields.One2many("ai.error", "file_id", string="Errores")
    record_ids = fields.One2many("ai.record", "file_id", string="Registros")
    skip = fields.Boolean(string="Saltar", default=False)

    def queue_file(self):
        domain = [
            ("file_id", "=", self.id),
            ("queued", "=", False),
            ("header", "=", False),
        ]
        all_records = self.env["ai.record"].search(domain)
        if not all_records:
            return

        first_record = all_records[0]
        has_tomany = self.env["ai.template.file.map"].has_tomany(first_record)
        size = (
            self.template_id.job_record_count or self.bundle_id.job_record_count or 100
        )

        if not has_tomany:
            record_count = len(all_records)
            for i in range(0, record_count, size):
                batch_records = all_records[i : i + size]
                self.env["ai.record.batch"].create(
                    {
                        "file_id": self.id,
                        "record_ids": [(6, 0, batch_records.ids)],
                    }
                )
        else:
            # Group records by col1 value (all records with same col1 go together)
            import logging
            _logger = logging.getLogger(__name__)
            
            # Group records by col1 value
            groups_dict = {}
            for record in all_records:
                col1_key = record.col1 or 'empty'  # Handle empty col1 values
                if col1_key not in groups_dict:
                    groups_dict[col1_key] = []
                groups_dict[col1_key].append(record.id)
            
            # Convert to list of groups
            groups = list(groups_dict.values())
            
            _logger.info(f"Total records: {len(all_records)}")
            _logger.info(f"Total groups created: {len(groups)}")
            for i, group in enumerate(groups):
                _logger.info(f"Group {i}: {len(group)} records")

            # Create batches from the groups
            current_batch_records_ids = []
            for group in groups:
                if len(current_batch_records_ids) + len(group) > size:
                    if current_batch_records_ids:
                        self.env["ai.record.batch"].create(
                            {
                                "file_id": self.id,
                                "record_ids": [(6, 0, current_batch_records_ids)],
                            }
                        )
                    current_batch_records_ids = group
                else:
                    current_batch_records_ids.extend(group)

            if current_batch_records_ids:
                self.env["ai.record.batch"].create(
                    {
                        "file_id": self.id,
                        "record_ids": [(6, 0, current_batch_records_ids)],
                    }
                )

        batch_ids = self.env["ai.record.batch"].search([("file_id", "=", self.id)])
        for batch_id in batch_ids:
            batch_id.queue_batch()
        self.queued = True
        return True
