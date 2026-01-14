from odoo import api, fields, models


class SaleReturnWizardLine(models.TransientModel):
    _name = "sale.order.return.wizard.line"
    _description = "Sale Order Return Wizard Line"

    product_id = fields.Many2one(
        "product.product",
        string="Product",
        required=True,
        domain="[('id', '=', product_id)]",
    )
    quantity = fields.Float(digits="Product Unit of Measure", required=True)
    uom_id = fields.Many2one(
        "uom.uom", string="Unit of Measure", related="product_id.uom_id"
    )
    move_id = fields.Many2one("stock.move", string="Move")
    wizard_id = fields.Many2one("sale.order.return.wizard", string="Wizard")


class SaleReturnWizard(models.TransientModel):
    _name = "sale.order.return.wizard"
    _description = "Sale Order Return Wizard"

    order_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sale Order",
        default=lambda self: self._context.get("order_id"),
    )

    order_return_wizard_lines = fields.One2many(
        comodel_name="sale.order.return.wizard.line",
        compute="_compute_data",
        readonly=False,
        inverse_name="wizard_id",
        string="Move Lines",
    )

    picking_ids = fields.Many2many(
        comodel_name="stock.picking",
        compute="_compute_data",
        string="Picking",
        readonly=False,
    )

    @api.depends("order_id", "order_id.order_line", "order_id.picking_ids")
    def _compute_data(self):
        for record in self:
            sale_lines_to_return = record.order_id.order_line.filtered(
                lambda line: line.product_uom_qty < 0
            )
            products = sale_lines_to_return.mapped("product_id")
            commercial_partner = record.order_id.partner_id.commercial_partner_id
            partner_ids = [commercial_partner.id]
            partner_ids.extend(commercial_partner.child_ids.ids)

            picking_ids = self.env["stock.picking"].search(
                [
                    ("state", "=", "done"),
                    ("picking_type_id.code", "=", "outgoing"),
                    ("partner_id", "in", partner_ids),
                    (
                        "location_dest_id.id",
                        "=",
                        record.order_id.partner_id.property_stock_customer.id,
                    ),
                    ("move_lines.product_id", "in", products.ids),
                ]
            )
            record.picking_ids = picking_ids
            record.order_return_wizard_lines = self.env["sale.order.return.wizard.line"]

            if record.picking_ids:
                return_lines = []
                for picking in record.picking_ids:
                    moves = picking.move_lines.filtered(
                        lambda m, products=products: m.product_id.id in products.ids
                    )
                    for move in moves:
                        sale_line = sale_lines_to_return.filtered(
                            lambda line, move=move: line.product_id == move.product_id
                        )
                        if sale_line:
                            return_lines.append(
                                (
                                    0,
                                    0,
                                    {
                                        "product_id": sale_line.product_id.id,
                                        "quantity": abs(sale_line.product_uom_qty),
                                        "uom_id": sale_line.product_uom.id,
                                        "move_id": move.id,
                                    },
                                )
                            )
                record.order_return_wizard_lines = return_lines

    def create_returns(self):
        ReturnPicking = self.env["stock.return.picking"]
        for picking in self.picking_ids:
            return_picking = ReturnPicking.with_context(
                active_id=picking.id, active_ids=[picking.id]
            ).create(
                {
                    "move_dest_exists": False,
                    "original_location_id": picking.location_id.id,
                    "location_id": picking.location_id.id,
                    "picking_id": picking.id,
                }
            )

            return_picking._onchange_picking_id()
            for return_line in self.order_return_wizard_lines:
                return_move = return_picking.product_return_moves.filtered(
                    lambda m, return_line=return_line: m.product_id.id
                    == return_line.product_id.id
                )
                if return_move:
                    return_move.quantity = return_line.quantity

            products = self.order_return_wizard_lines.mapped("product_id")
            return_picking.product_return_moves.filtered(
                lambda m, products=products: m.product_id.id not in products.ids
            ).unlink()

            return_picking.create_returns()
