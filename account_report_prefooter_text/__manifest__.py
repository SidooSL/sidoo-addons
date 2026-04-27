{
    "name": "Account Report Prefooter Text",
    "version": "18.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Add configurable HTML text before footer in customer and vendor invoices PDF",
    "description": """
        Account Report Prefooter Text
        =============================

        Adds configurable HTML fields in Settings to display custom text
        before the footer in PDF invoices:

        - Customer Invoice Prefooter Text: Shown in customer invoices (out_invoice, out_refund)
        - Vendor Bill Prefooter Text: Shown in vendor bills (in_invoice, in_refund)

        Configuration available in Accounting > Configuration > Settings.
    """,
    "author": "Jorge Quinteros, SDi",
    "website": "https://www.sdi.es",
    "license": "LGPL-3",
    "depends": [
        "account",
        "web",
    ],
    "data": [
        "views/res_config_settings_views.xml",
        "report/report_external_layout.xml",
    ],
}
