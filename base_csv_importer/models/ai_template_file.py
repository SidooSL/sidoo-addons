from odoo import fields, models


class AITemplateFile(models.Model):
    _name = "ai.template.file"
    _description = "AI Template File"

    type_id = fields.Many2one("ai.import.type", string="Tipo de Importación")
    name = fields.Char(string="Prefijo del Fichero")
    job_record_count = fields.Integer(string="Cantidad de registros por job")
    mapper_id = fields.Many2one("ai.template.file.map", string="Mapeador")
    sequence = fields.Integer(string="Secuencia")
