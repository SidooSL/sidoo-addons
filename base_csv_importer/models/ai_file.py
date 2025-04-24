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
        record_count = self.env["ai.record"].search_count(domain)
        if not record_count:
            return
        size = (
            self.template_id.job_record_count or self.bundle_id.job_record_count or 100
        )
        for i in range(0, record_count, size):
            batch_records = self.env["ai.record"].search(domain, limit=size, offset=i)
            batch_id = self.env["ai.record.batch"].create(
                {
                    "file_id": self.id,
                    "record_ids": [(6, 0, batch_records.ids)],
                }
            )
        first_record = self.env["ai.record"].search(domain, limit=1)
        has_tomany = self.env["ai.template.file.map"].has_tomany(first_record)
        batch_ids = self.env["ai.record.batch"].search(
            [
                ("file_id", "=", self.id),
            ]
        )
        if has_tomany and batch_ids:
            previous_batch_id = batch_ids[0]
            for batch_id in batch_ids:
                if batch_id != previous_batch_id:
                    for record in batch_id.record_ids:
                        if not record.col1:
                            record.batch_id = previous_batch_id
                        else:
                            break
                previous_batch_id = batch_id

        for batch_id in batch_ids:
            batch_id.queue_batch()
        self.queued = True
        return True
