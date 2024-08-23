# Copyright 2024 Sidoo
#                Luis Adan Jimenez Hernandez <ljimenez@sidoo.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


{
    "name": "Account Move Excel to JSON",
    "version": "16.0.1.0.1",
    "license": "AGPL-3",
    "category": "Accounting",
    "sequence": 1,
    "complexity": "easy",
    "author": "Sidoo",
    "depends": ["base", "account"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/wizard_excel_to_json_view.xml",
    ],
    "external_dependencies": {
        "python": ["pandas"],
    },
    "installable": True,
}
