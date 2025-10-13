from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    sale_line_purchase_price = fields.Float(
        string="Unit Purchase Price",
        digits="Product Price",
        help="The purchase price unit of the product for this stock move.",
    )
