from odoo import fields, models, api, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_returnable = fields.Boolean(
        default=False,
    )

    @api.onchange('type')
    def onchange_type(self):
        if self.type != 'consu':
            self.is_returnable = False
