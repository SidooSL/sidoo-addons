from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    customer_invoice_footer_text = fields.Html(
        related="company_id.customer_invoice_footer_text",
        string="Customer Invoice Footer Text",
        readonly=False,
        help="This text will be displayed before the footer in customer invoices and credit notes PDF.",
    )
    vendor_bill_footer_text = fields.Html(
        related="company_id.vendor_bill_footer_text",
        string="Vendor Bill Footer Text",
        readonly=False,
        help="This text will be displayed before the footer in vendor bills and refunds PDF.",
    )
