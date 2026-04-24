# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class WhatsappAccount(models.Model):
    _inherit = "whatsapp.account"

    whatsapp_member_manager_ids = fields.Many2many(
        comodel_name="res.users",
        relation="whatsapp_account_member_manager_rel",
        column1="account_id",
        column2="user_id",
        string="Member Managers",
        domain=lambda self: [
            (
                "groups_id",
                "in",
                [
                    self.env.ref(
                        "whatsapp_conversation_extension.group_whatsapp_member_manager",
                        raise_if_not_found=False,
                    ).id
                ],
            )
        ],
        help="Users who can edit the members of all conversations linked to this WhatsApp account.",
    )
