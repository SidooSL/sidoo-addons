from odoo import api, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model_create_multi
    def create(self, vals_list):
        partners = super().create(vals_list)
        partners._start_automatic_tier_validation()
        return partners

    def write(self, vals):
        must_restart_validation = bool(
            set(vals).intersection(self._partner_tier_revalidation_fields(vals))
        )
        if (
            vals.get("active")
            and not self.env.context.get("automatic_tier_validation")
            and any(
                partner.need_validation
                or partner.validation_status in ("waiting", "pending", "rejected")
                for partner in self
            )
        ):
            raise ValidationError(
                self.env._(
                    "A contact pending approval cannot be unarchived. "
                    "Complete its tier validation first."
                )
            )
        result = super().write(vals)
        if not self.env.context.get("automatic_tier_validation"):
            if must_restart_validation:
                self.restart_validation()
            self._start_automatic_tier_validation()
        return result

    def _start_automatic_tier_validation(self):
        """Submit applicable draft contacts and keep them unavailable."""
        partners = self.filtered(lambda partner: partner.need_validation)
        if not partners:
            return
        partners.request_validation()
        partners.with_context(
            automatic_tier_validation=True, skip_validation_check=True
        ).write({"active": False})

    def _get_automatic_approved_stage(self):
        return self.env["res.partner.stage"].search(
            [("state", "=", "confirmed")], order="sequence, id", limit=1
        )

    def _validate_tier(self, reviews):
        result = super()._validate_tier(reviews)
        self.invalidate_recordset(["validation_status"])
        if self.validation_status == "validated":
            approved_stage = self._get_automatic_approved_stage()
            values = {"active": True}
            if approved_stage:
                values["stage_id"] = approved_stage.id
            self.with_context(
                automatic_tier_validation=True, skip_validation_check=True
            ).write(values)
        return result
