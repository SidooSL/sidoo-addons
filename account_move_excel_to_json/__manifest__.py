# Copyright 2024 Sidoo
#                Luis Adan Jimenez Hernandez <ljimenez@sidoo.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


{
    "name": "Account Move Excel to JSON",
    "version": "17.0.1.0.1",
    "license": "AGPL-3",
    "category": "Accounting",
    "sequence": 1,
    "complexity": "easy",
    "author": "Luis Jimenez, Sidoo Soluciones S.L.",
    "depends": ["base", "account", "account_move_template"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/wizard_excel_to_json_view.xml",
    ],
    "external_dependencies": {
        "python": ["pandas", "openpyxl"],
    },
    "installable": True,
}
