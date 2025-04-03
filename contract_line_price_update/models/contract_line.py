from odoo import _, fields, models


class ContractLine(models.Model):
    _name = "contract.line"
    _inherit = ["contract.line", "mail.thread"]

    prev_price = fields.Float(
        string="Previous Price",
        help="Previous price of the contract line",
    )
    last_mass_update_date = fields.Datetime(
        help="Last time this contract line was updated in a mass update",
    )

    def action_contract_line_update_wizard(self):
        return {
            "name": _("Update Contract Line Prices"),
            "type": "ir.actions.act_window",
            "res_model": "contract.line.update.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_contract_line_ids": self.ids,
                "default_output_type": "_contract_line_output",
            },
        }
