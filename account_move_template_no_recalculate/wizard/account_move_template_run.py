# Copyright 2015-2019 See manifest
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models


class AccountMoveTemplateRun(models.TransientModel):
    _inherit = "account.move.template.run"
    _description = "Wizard to generate move from template"

    # STEP 1
    def load_lines(self):
        result = super().load_lines()
        if not self.template_id.recalculate:
            result["context"] = dict(result.get("context", {}), no_recalculate=True)
        return result
