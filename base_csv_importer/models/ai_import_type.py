from odoo import fields, models


class AiImportType(models.Model):
    _name = "ai.import.type"
    _description = "AI Import Type"

    name = fields.Char(string="Nombre")
    bundle_ids = fields.One2many(
        "ai.file.bundle", "type_id", string="Históricos importados"
    )
    template_ids = fields.One2many("ai.template.file", "type_id", string="Plantillas")
