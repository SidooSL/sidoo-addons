from odoo import fields, models


class AIError(models.Model):
    _name = "ai.error"
    _description = "AI Error"

    name = fields.Char(string="Nombre")
    stacktrace = fields.Text(string="Traza")
    record_id = fields.Many2one("ai.record", string="Registro")
    bundle_id = fields.Many2one(
        related="record_id.file_id.bundle_id", string="Histórico"
    )
    file_id = fields.Many2one(related="record_id.file_id", string="Fichero")
    batch_id = fields.Many2one(related="record_id.batch_id", string="Lote")
