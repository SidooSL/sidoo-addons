from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def open_picking_return(self):
        self.ensure_one()
        return {
            "name": "Return Picking",
            "type": "ir.actions.act_window",
            "res_model": "stock.return.picking",
            "view_mode": "form",
            "target": "new",
            "context": {
                "active_id": self.id,
                "active_ids": [self.id],
            },
        }
