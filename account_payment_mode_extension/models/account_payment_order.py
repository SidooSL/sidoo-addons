from odoo import models


class AccountPaymentOrder(models.Model):
    _inherit = "account.payment.order"

    def draft2open(self):
        res = super().draft2open()
        account_id = self.env.ref(
            f"account.{self.company_id.id}_account_common_4312",
            raise_if_not_found=False,
        )
        for order in self:
            if order.payment_mode_id.compensation_account:
                lines = self.env["account.move.line"]
                for move in order.move_ids:
                    line = move.line_ids.filtered(
                        lambda x, account_id=account_id: x.account_id.id
                        == account_id.id
                    )
                    lines += line
                lines.account_id = order.payment_mode_id.transition_account_id.id
        return res
