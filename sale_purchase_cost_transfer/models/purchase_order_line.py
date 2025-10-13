from odoo import api, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.model
    def _prepare_purchase_order_line_from_procurement(
        self, product_id, product_qty, product_uom, company_id, values, po
    ):
        """Override to set purchase price from procurement values"""
        res = super()._prepare_purchase_order_line_from_procurement(
            product_id, product_qty, product_uom, company_id, values, po
        )
        if values.get("move_dest_ids") and res.get("product_qty"):
            price_unit = 0.0
            moves = values["move_dest_ids"]
            for move in moves:
                price_unit += move.sale_line_purchase_price * move.product_qty
            price_unit = price_unit / res["product_qty"]
            if price_unit:
                res["price_unit"] = price_unit
        return res
