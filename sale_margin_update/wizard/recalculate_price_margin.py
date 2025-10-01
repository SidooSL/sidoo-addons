# Copyright 2024 SDi Sidoo Soluciones S.L. <www.sidoo.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleRecalculatePriceMargin(models.TransientModel):
    _name = "sale.recalculate.price.margin"
    _description = "Recalculate Price By Margin"

    sale_margin_percent = fields.Float(
        string="Margin (%)",
        digits="Product Price",
        required=True,
    )
    line_id = fields.Many2one("sale.order.line", ondelete="cascade")
    order_id = fields.Many2one("sale.order", ondelete="cascade")

    @api.constrains("sale_margin_percent")
    def _check_sale_margin_percent(self):
        for record in self:
            if record.sale_margin_percent < 0:
                raise ValidationError(_("Margin can't be negative"))
            if record.sale_margin_percent >= 100:
                raise ValidationError(_("Margin can't be greater than 100"))

    def recalculate_price_margin(self):
        self.ensure_one()
        lines = self.line_id if self.line_id else self.order_id.order_line

        updated_lines = 0
        for line in lines.filtered(lambda x: x.product_id and x.purchase_price > 0):
            # Calculate price subtotal based on margin
            if self.sale_margin_percent == 100:
                price_subtotal = (line.purchase_price * line.product_uom_qty) * 2
            elif self.sale_margin_percent == 0:
                price_subtotal = line.purchase_price * line.product_uom_qty
            else:
                margin_factor = 1 - (self.sale_margin_percent / 100)
                if margin_factor <= 0:
                    continue  # Skip invalid margin calculations
                price_subtotal = (
                    line.purchase_price * line.product_uom_qty
                ) / margin_factor

            # Calculate unit price considering discount
            if line.product_uom_qty > 0:
                price_unit_with_discount = price_subtotal / line.product_uom_qty
                discount_factor = 1 - (line.discount / 100)
                if discount_factor > 0:
                    line.price_unit = price_unit_with_discount / discount_factor
                    updated_lines += 1

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Margin Updated"),
                "message": _("%s line(s) updated successfully.") % updated_lines,
                "type": "success",
                "next": {"type": "ir.actions.act_window_close"},
            },
        }
