from odoo import models


class AccountPaymentOrder(models.Model):
    _inherit = "account.payment.order"

    def _prepare_move(self, payments=None):
        vals = super()._prepare_move(payments=payments)
        if self.payment_mode_id.compensation_account:
            transition_account_id = self.payment_mode_id.transition_account_id
            for line in vals.get("line_ids", []):
                *_, line_vals = line
                if line_vals.get("account_id", False):
                    line_vals.update({"account_id": transition_account_id.id})
        return vals
