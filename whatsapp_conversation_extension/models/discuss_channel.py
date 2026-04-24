# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import AccessError


class DiscussChannel(models.Model):
    _inherit = "discuss.channel"

    can_manage_whatsapp_members = fields.Boolean(
        compute="_compute_can_manage_whatsapp_members",
        string="Can Manage Members",
        help="True if the current user belongs to the member manager group AND is assigned as manager of the WhatsApp account linked to this channel.",
    )

    @api.depends("wa_account_id", "wa_account_id.whatsapp_member_manager_ids")
    @api.depends_context("uid")
    def _compute_can_manage_whatsapp_members(self):
        user = self.env.user
        is_in_group = user.has_group(
            "whatsapp_conversation_extension.group_whatsapp_member_manager"
        )
        for channel in self:
            channel.can_manage_whatsapp_members = (
                is_in_group
                and user in channel.wa_account_id.whatsapp_member_manager_ids
            )

    def action_open_whatsapp_channel_form(self):
        """Open the minimal backend form view of this WhatsApp channel.

        Access is granted only if the current user belongs to the
        group_whatsapp_member_manager group AND is assigned as manager
        of this specific channel.
        """
        self.ensure_one()
        if not self.can_manage_whatsapp_members:
            raise AccessError(
                _(
                    "You do not have permission to manage the members of this WhatsApp conversation. "
                    'You must belong to the "WhatsApp Channel Member Manager" group '
                    "and be assigned as a manager for this channel."
                )
            )
        return {
            "type": "ir.actions.act_window",
            "name": self.name,
            "res_model": "discuss.channel",
            "res_id": self.id,
            "view_mode": "form",
            "view_id": self.env.ref(
                "whatsapp_conversation_extension.discuss_channel_view_form_whatsapp_minimal"
            ).id,
            "target": "current",
        }
