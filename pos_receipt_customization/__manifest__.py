{
    "name": "POS Receipt Customization",
    "version": "18.0.1.0.0",
    "category": "Point of Sale",
    "summary": "Customize POS receipt header and footer",
    "description": """
        Customizes POS receipt appearance by:
        - Hiding company logo in receipt header to save space
        - Removing/replacing 'Powered by Odoo' text in receipt footer
        - Maintaining all other receipt functionality intact
    """,
    "author": "Jorge Quinteros",
    "website": "www.sdi.es",
    "depends": ["point_of_sale"],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_receipt_customization/static/src/xml/receipt_templates.xml",
        ],
    },
    "license": "LGPL-3",
}
