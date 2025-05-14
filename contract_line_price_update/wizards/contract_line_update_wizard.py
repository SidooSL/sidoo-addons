from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ContractLineUpdateWizard(models.TransientModel):
    _name = "contract.line.update.wizard"
    _description = "Contract Line Update Wizard"

    contract_line_ids = fields.Many2many(
        comodel_name="contract.line",
        string="Contract Lines",
        required=True,
    )
    factor = fields.Float(
        string="Multiplier",
        digits=(16, 3),
        required=True,
    )

    count_line = fields.Integer(
        string="Number of Lines",
        compute="_compute_count_line",
        store=True,
    )

    @api.depends("contract_line_ids")
    def _compute_count_line(self):
        for wizard in self:
            wizard.count_line = len(wizard.contract_line_ids)

    def update_price(self):
        if self.factor == 0:
            raise UserError(_("The factor must be different from 0"))
        if len(self.contract_line_ids) == 0:
            raise UserError(_("No contract lines selected"))

        return {
            "type": "ir.actions.act_window",
            "res_model": "contract.line.update.confirm.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_contract_line_ids": self.contract_line_ids.ids,
                "default_factor": self.factor,
                "default_count_line": self.count_line,
                "default_output_type": self.env.context.get("default_output_type"),
            },
        }
