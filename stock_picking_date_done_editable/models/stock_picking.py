from odoo import fields, models


class Picking(models.Model):
    _inherit = "stock.picking"

    date_done = fields.Datetime(
        readonly=False,
    )
