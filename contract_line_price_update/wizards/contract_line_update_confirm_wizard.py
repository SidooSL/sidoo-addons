from odoo import fields, models, _


class ContractLineUpdateConfirmWizard(models.TransientModel):
    _name = 'contract.line.update.confirm.wizard'
    _description = 'Confirmation Wizard for Contract Line Update'

    contract_line_ids = fields.Many2many('contract.line', string='Contract Lines', required=True)
    factor = fields.Float('Multiplier', required=True)
    output_type = fields.Selection([
        ("_contract_output", "Contract"),
        ("_contract_line_output", "Contract Line"),
    ], string="To show", required=True)
    count_line = fields.Integer('Number of Lines')

    def confirm_update(self):
        for line in self.contract_line_ids:
            old_price = line.price_unit
            new_price = old_price * self.factor
            line.write({
                'prev_price': old_price,
                'price_unit': new_price,
                'last_mass_update_date': fields.Datetime.now(),
            })
            self._post_edit_info_message(line, old_price, new_price)
        return getattr(self, self.output_type)()

    def _post_edit_info_message(self, line, old_price, new_price):
        currency = line.currency_id
        if currency.position == "before":
            old_price_formatted = f"{currency.symbol}{old_price:.2f}"
            new_price_formatted = f"{currency.symbol}{new_price:.2f}"
        else:
            old_price_formatted = f"{old_price:.2f}{currency.symbol}"
            new_price_formatted = f"{new_price:.2f}{currency.symbol}"
        body = _(
            "Price updated from <b>%(old_price)s</b> to <b>%(new_price)s</b> using a factor of <b>%(factor).3f</b>"
        ) % {
            "old_price": old_price_formatted,
            "new_price": new_price_formatted,
            "factor": self.factor,
        }
        body_contract = body + _(" in contract line: <b>%s</b>") % (line.name)
        line.message_post(body=body)
        line.contract_id.message_post(body=body_contract)

    def _contract_output(self):
        return {
            "name": _("Updated Contract"),
            "type": "ir.actions.act_window",
            "res_model": "contract.contract",
            "view_mode": "tree,form",
            "target": "current",
            "domain": [("id", "=", self.contract_line_ids.mapped("contract_id").ids)],
        }

    def _contract_line_output(self):
        return {
            "name": _("Updated Contract Line"),
            "type": "ir.actions.act_window",
            "res_model": "contract.line",
            "view_mode": "tree,form",
            "target": "current",
            "domain": [("id", "in", self.contract_line_ids.ids)],
        }
