# Copyright 2015-2019 See manifest
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class AccountMoveTemplate(models.Model):
    _inherit = "account.move.template"
    _description = "Journal Entry Template"

    recalculate = fields.Boolean(
        default=True,
        help="If checked, create new lines for the taxes",
    )
