from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    payment_move_ids = fields.Many2many(
        "account.move",
        relation="account_move_payment_for_importer_rel",
        column1="source_move_id",
        column2="destination_move_id",
    )

    def action_reconcile(self):
        for move_id in self:
            if not self.env.context.get("skip_remove_reconcile", False):
                move_id.line_ids.remove_move_reconcile()
            for invoice in move_id.filtered(lambda move: move.is_invoice()):
                move_lines = invoice.payment_move_ids.line_ids.filtered(
                    lambda line, partner_id=invoice.partner_id.id: line.account_type
                    in ("asset_receivable", "liability_payable")
                    and not line.reconciled
                    and (line.partner_id.id == partner_id or not line.partner_id)
                )
                for line in move_lines:
                    invoice.js_assign_outstanding_line(line.id)
