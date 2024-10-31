from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def open_wizard_returns(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.order.return.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "order_id": self.id,
            },
        }
