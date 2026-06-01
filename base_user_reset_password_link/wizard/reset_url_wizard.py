from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError


class ResetUrlWizard(models.TransientModel):
    _name = "reset.url.wizard"
    _description = "Wizard to display password reset URL"

    user_id = fields.Many2one("res.users", string="User", readonly=True)
    user_name = fields.Char(string="Name", readonly=True)
    reset_url = fields.Char(string="Reset URL", readonly=True)
    hours_to_expire = fields.Integer(string="Hours Until Expiration", readonly=True)
    expires_at = fields.Datetime(string="Expires At", readonly=True)

    @api.model
    def _get_reset_password_validity_hours(self):
        value = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "auth_signup.reset_password.validity.hours",
                default="4",
            )
        )
        try:
            return max(int(value), 1)
        except (TypeError, ValueError):
            return 4

    @api.model
    def generate_for_user(self, user_id):
        if not self.env.user.has_group("base.group_erp_manager"):
            raise AccessError(_("You are not allowed to generate password reset URLs."))

        user = self.env["res.users"].browse(user_id)

        if not user.exists():
            raise UserError(_("User not found."))
        if not user.active:
            raise UserError(_("Cannot generate a link for an archived user."))
        if not user.partner_id:
            raise UserError(_("The user has no related contact."))

        partner = user.partner_id.sudo()
        partner.signup_prepare(signup_type="reset")

        url = (
            partner.with_context(signup_force_type_in_url="reset")
            ._get_signup_url_for_action()
            .get(partner.id)
        )

        if not url:
            raise UserError(_("Could not generate the reset URL."))

        validity_hours = self._get_reset_password_validity_hours()
        expires_at = fields.Datetime.now() + timedelta(hours=validity_hours)

        wizard = self.create(
            {
                "user_id": user.id,
                "user_name": user.name,
                "reset_url": url,
                "hours_to_expire": validity_hours,
                "expires_at": expires_at,
            }
        )

        return {
            "type": "ir.actions.act_window",
            "name": _("Password Reset URL"),
            "res_model": "reset.url.wizard",
            "res_id": wizard.id,
            "view_mode": "form",
            "target": "new",
        }
