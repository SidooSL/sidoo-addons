from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_reconcile(self):
        for move_id in self:
            payments = move_id.matched_payment_ids
            move_id.write(
                {
                    "matched_payment_ids": None,
                }
            )
            for invoice in move_id.filtered(lambda move: move.is_invoice()):
                move_lines = payments.move_id.line_ids.filtered(
                    lambda line: line.account_type
                    in ("asset_receivable", "liability_payable")
                    and not line.reconciled
                )
                for line in move_lines:
                    invoice.js_assign_outstanding_line(line.id)
