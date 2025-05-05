from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def action_unreconcile_all(self):
        for partner in self:
            partner.with_delay().action_unreconcile()

    def action_unreconcile(self):
        date_from = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("customize.date_from", default="2021-01-01")
        )
        date_to = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("customize.date_to", default="2021-12-31")
        )
        line_ids = self.env["account.move.line"].search(
            [
                ("partner_id", "=", self.id),
                ("reconciled", "=", True),
                ("date", ">=", date_from),
                ("date", "<=", date_to),
            ]
        )
        for line_id in line_ids:
            line_id.remove_move_reconcile()
