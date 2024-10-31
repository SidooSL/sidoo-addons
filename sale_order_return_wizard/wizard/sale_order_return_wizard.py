from odoo import fields, models, api


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
        inverse_name="wizard_id",
        string="Move Lines",
    )

    picking_id = fields.Many2one(
        comodel_name="stock.picking", compute="_compute_data", string="Picking"
    )

    @api.depends("order_id", "order_id.order_line", "order_id.picking_ids")
    def _compute_data(self):
        for record in self:
            sale_lines_to_return = record.order_id.order_line.filtered(
                lambda line: line.product_uom_qty < 0
            )
            products = sale_lines_to_return.mapped("product_id")
            picking_ids = record.order_id.picking_ids.filtered(
                lambda p: p.state == "done"
                and p.picking_type_id.code == "outgoing"
                and p.partner_id.id == record.order_id.partner_id.id
                and p.sale_id.id == record.order_id.id
                and p.move_lines.filtered(lambda ml: ml.product_id.id in products.ids)
            )
            record.picking_id = picking_ids[0] if picking_ids else False
            record.order_return_wizard_lines = self.env["sale.order.return.wizard.line"]

            if record.picking_id:
                moves = record.picking_id.move_lines.filtered(
                    lambda m: m.product_id.id in products.ids
                )
                # Crear las líneas de devolución
                return_lines = []
                for sale_line in sale_lines_to_return:
                    move = moves.filtered(
                        lambda m: m.product_id == sale_line.product_id
                    )
                    move_id = move[0].id if move else False
                    return_lines.append(
                        (
                            0,
                            0,
                            {
                                "product_id": sale_line.product_id.id,
                                "quantity": abs(sale_line.product_uom_qty),
                                "uom_id": sale_line.product_uom.id,
                                "move_id": move_id,
                            },
                        )
                    )
                record.order_return_wizard_lines = return_lines

    def create_returns(self):
        ReturnPicking = self.env["stock.return.picking"]
        for wizard in self:
            if not wizard.picking_id:
                continue

            return_picking = ReturnPicking.with_context(
                active_id=wizard.picking_id.id, active_ids=[wizard.picking_id.id]
            ).create(
                {
                    "move_dest_exists": False,
                    "original_location_id": wizard.picking_id.location_id.id,
                    "location_id": wizard.picking_id.location_id.id,
                    "picking_id": wizard.picking_id.id,
                }
            )

            return_picking._onchange_picking_id()
            for return_line in wizard.order_return_wizard_lines:
                return_move = return_picking.product_return_moves.filtered(
                    lambda m: m.product_id.id == return_line.product_id.id
                )
                if return_move:
                    return_move.quantity = return_line.quantity

            products = wizard.order_return_wizard_lines.mapped("product_id")
            return_picking.product_return_moves.filtered(
                lambda m: m.product_id.id not in products.ids
            ).unlink()

            return return_picking.create_returns()
