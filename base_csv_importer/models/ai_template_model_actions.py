import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class AITemplateFileMap(models.Model):
    _name = "ai.template.model.actions"
    _description = "After Import actions by model"

    sequence = fields.Integer(
        string="Sequence",
        default=10,
        help="Orden de ejecución de las acciones",
    )
    mapper_id = fields.Many2one(
        "ai.template.file.map",
        string="Template",
        required=True,
        ondelete="cascade",
    )
    action = fields.Text(
        string="Lambda",
        help="Lambda to execute after import",
    )
