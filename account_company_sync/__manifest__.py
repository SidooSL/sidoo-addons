# Copyright 2024 Sidoo
#                Luis Adan Jimenez Hernandez <ljimenez@sidoo.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


{
    "name": "Account Company Sync",
    "version": "17.0.1.0.1",
    "license": "AGPL-3",
    "category": "Accounting",
    "sequence": 1,
    "complexity": "easy",
    "author": "Luis Jimenez, Sidoo Soluciones S.L.",
    "depends": ["base", "account"],
    "data": [
        "security/ir.model.access.csv",
        "views/account_account_views.xml",
        "wizard/wizard_account_company_sync_views.xml",
    ],
    "installable": True,
}
