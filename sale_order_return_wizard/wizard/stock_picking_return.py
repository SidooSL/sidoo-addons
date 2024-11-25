# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ReturnPickingLine(models.TransientModel):
    _inherit = "stock.return.picking.line"

    lot_id = fields.Many2one(
        comodel_name="stock.production.lot", compute="_compute_lot"
    )
    package_id = fields.Many2one(
        comodel_name="product.packaging",
        compute="_compute_package",
        readonly=False,
        store=True,
    )

    @api.depends("product_id", "wizard_id.picking_id")
    def _compute_lot(self):
        for line in self:
            picking_id = line.wizard_id.picking_id
            lot_id = picking_id.move_line_ids_without_package.filtered(
                lambda x, line=line: x.product_id == line.product_id
            ).lot_id
            line.lot_id = lot_id

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
        return picking_id, picking_type
