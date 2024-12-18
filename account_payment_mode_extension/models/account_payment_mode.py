from odoo import fields, models


class AccountPaymentMode(models.Model):
    _inherit = "account.payment.mode"

    compensation_account = fields.Boolean(default=False)

    transition_account_id = fields.Many2one(comodel_name="account.account")
