from odoo import models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def link_move(self):
        odoo_vals = self.env.context["odoo_vals"]
        if self.state != "paid":
            account_move_id = (
                self.env["account.move"]
                .with_context(skip_readonly_check=True)
                .browse(odoo_vals.get("move_id", None))
            )
            if account_move_id and not account_move_id.partner_id:
                account_move_id.partner_id = self.partner_id.id
                account_move_id.line_ids.write(
                    {
                        "partner_id": self.partner_id.id,
                    }
                )
            self.move_id = account_move_id
