from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sent_date = fields.Datetime(
        string="Sent Date",
        copy=False,
        readonly=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        now = fields.Datetime.now()
        for vals in vals_list:
            if vals.get("state") == "sent":
                vals["sent_date"] = now
        return super().create(vals_list)

    def write(self, vals):
        if vals.get("state") != "sent":
            return super().write(vals)

        orders_to_mark = self.filtered(lambda order: order.state != "sent")
        result = super().write(vals)
        if orders_to_mark:
            orders_to_mark.filtered(lambda order: order.state == "sent").write(
                {"sent_date": fields.Datetime.now()}
            )
        return result
