# Copyright 2024 Sidoo
#                Luis Adan Jimenez Hernandez <ljimenez@sidoo.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


{
    "name": "Sale Order Return Wizard",
    "version": "14.0.1.0.1",
    "license": "AGPL-3",
    "category": "Sales",
    "sequence": 1,
    "complexity": "easy",
    "author": "Luis Adan Jimenez Hernandez, Sidoo Soluciones S.L.",
    "depends": ["sale", "stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_order_view.xml",
        "wizard/sale_order_return_wizard_view.xml",
    ],
    "installable": True,
}
