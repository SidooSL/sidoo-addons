# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models


class ReturnPickingLine(models.TransientModel):
    _inherit = "stock.return.picking.line"

    package_id = fields.Many2one(
        comodel_name="product.packaging",
        compute="_compute_package",
        readonly=False,
        store=True,
    )

    @api.depends("product_id", "wizard_id.picking_id")
    def _compute_package(self):
        for line in self:
            picking_id = line.wizard_id.picking_id
            package_id = picking_id.move_ids_without_package.filtered(
                lambda x, line=line: x.product_id == line.product_id
            ).product_packaging
            line.package_id = package_id


class ReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    def _create_returns(self):
        picking_id, picking_type = super()._create_returns()
        # if package is removed in stock.return.picking.line, remove it from picking too
        for return_line in self.product_return_moves:
            if not return_line.package_id:
                picking = self.env["stock.picking"].browse(picking_id)
                move = picking.move_ids_without_package.filtered(
                    lambda x, return_line=return_line: x.product_id
                    == return_line.product_id
                )
                move.write(
                    {
                        "product_packaging": False,
                        "product_packaging_qty": 0,
                        "product_uom_qty": return_line.quantity,
                    }
                )

        self._post_return_message_to_order(picking_id)
        return picking_id, picking_type

    def _post_return_message_to_order(self, return_picking_id):
        return_picking = self.env["stock.picking"].browse(return_picking_id)
        order_id = self._context.get("order_id")
        sale_order = self.env["sale.order"].browse(order_id) if order_id else None

        if not sale_order:
            return

        returned_products_html = "<ul>"
        for line in self.product_return_moves:
            if line.quantity > 0:
                returned_products_html += (
                    f"<li>{line.product_id.display_name}: "
                    f"{line.quantity} {line.uom_id.name}</li>"
                )
        returned_products_html += "</ul>"

        picking_link = (
            f'<a href="#" data-oe-model="stock.picking" '
            f'data-oe-id="{return_picking.id}">{return_picking.name}</a>'
        )

        message_body = (
            f"<p><strong>{_('Devolución creada desde este pedido')}</strong></p>"
            f"<p>{_('Productos devueltos:')}</p>"
            f"{returned_products_html}"
            f"<p>{_('Enlace al albarán de devolución:')} {picking_link}</p>"
        )

        sale_order.message_post(
            body=message_body,
            subject=_("Devolución Creada"),
            message_type="notification",
        )
