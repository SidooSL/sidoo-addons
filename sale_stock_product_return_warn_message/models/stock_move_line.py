from odoo import fields, models, api, _


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    is_returnable = fields.Boolean(
        related='product_id.product_tmpl_id.is_returnable',
        store=True,
    )
