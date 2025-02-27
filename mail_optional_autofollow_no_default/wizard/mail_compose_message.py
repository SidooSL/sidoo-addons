from odoo import api, models


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        res["autofollow_recipients"] = False
        return res
