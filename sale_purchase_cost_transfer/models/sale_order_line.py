from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model
    def _prepare_procurement_values(self, group_id=False):
        """Override to pass purchase price in procurement values"""
        values = super()._prepare_procurement_values(group_id)
        if self.purchase_price:
            values["sale_line_purchase_price"] = self.purchase_price
        return values
