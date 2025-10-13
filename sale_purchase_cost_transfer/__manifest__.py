{
    "name": "Sale Purchase Cost Transfer",
    "version": "17.0.1.0.0",
    "category": "Sales/Purchase",
    "summary": 'Transfer purchase price, "cost", to purchase order line unit cost',
    "license": "LGPL-3",
    "description": """
Transfer Purchase Price to Purchase Order Line
==============================================

When a sale order is confirmed and generates purchase order lines,
this module transfers the purchase_price field value from the sale
order line to the unit cost (price_unit) of the generated purchase
order line.

Features:
- Automatic price transfer on sale order confirmation
- Maintains cost tracking between sales and purchases
- Works with existing purchase order generation workflows
    """,
    "depends": [
        "sale",
        "sale_margin",
        "purchase",
        "sale_purchase",
    ],
    "data": [],
    "installable": True,
    "auto_install": False,
    "application": False,
}
