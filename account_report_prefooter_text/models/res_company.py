from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    customer_invoice_footer_text = fields.Html(
        string="Customer Invoice Footer Text",
        translate=True,
        help="This text will be displayed before the footer in customer invoices and credit notes PDF.",
    )
    vendor_bill_footer_text = fields.Html(
        string="Vendor Bill Footer Text",
        translate=True,
        help="This text will be displayed before the footer in vendor bills and refunds PDF.",
    )
