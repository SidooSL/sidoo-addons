from odoo import _, models


class Contract(models.Model):
    _inherit = "contract.contract"

    def action_open_price_update_wizard(self):
        contract_lines = self.mapped("contract_line_ids")

        return {
            "name": _("Update Contract Line Prices"),
            "type": "ir.actions.act_window",
            "res_model": "contract.line.update.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_contract_line_ids": contract_lines.ids,
                "default_output_type": "_contract_output",
            },
        }
