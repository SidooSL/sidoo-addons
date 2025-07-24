###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import models
from odoo.tools.safe_eval import safe_eval


class ResPartner(models.Model):
    _inherit = "res.partner"

    def action_see_opportunity_attachments(self):
        domain = [
            ("res_model", "=", "crm.lead"),
            ("res_id", "in", self.opportunity_ids.ids),
        ]
        action = self.env["ir.actions.actions"]._for_xml_id("base.action_attachment")
        context = action.get("context", "{}")
        context = safe_eval(context)
        context["create"] = False
        context["edit"] = False
        action.update({"domain": domain, "context": context})
        return action
