from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    is_returnable = fields.Boolean(
        compute="_compute_is_returnable",
        store=True,
    )

    warning_message = fields.Char(
        readonly=True,
        compute="_compute_warning_message",
        store=True,
    )

    @api.depends("is_returnable")
    def _compute_warning_message(self):
        warning_param = (
            self.env["ir.config_parameter"].sudo().get_param("returnable.message")
        )
        for picking in self:
            if picking.is_returnable:
                picking.warning_message = warning_param
            else:
                picking.warning_message = False

    @api.depends("move_line_ids.is_returnable")
    def _compute_is_returnable(self):
        for picking in self:
            picking.is_returnable = any(
                line.is_returnable for line in picking.move_line_ids
            )
