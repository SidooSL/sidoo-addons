# Copyright 2024 Sidoo
#                Luis Adan Jimenez Hernandez <ljimenez@sidoo.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


{
    "name": "Account Company Sync",
    "version": "16.0.1.0.1",
    "license": "AGPL-3",
    "category": "Accounting",
    "sequence": 1,
    "complexity": "easy",
    "author": "Luis Jimenez, Sidoo Soluciones S.L.",
    "depends": ["base", "web", "account", "queue_job"],
    "data": [
        "security/ir.model.access.csv",
        "data/account_account_channel.xml",
        "data/account_account_job_function.xml",
        "views/account_account_views.xml",
        "wizard/wizard_account_company_sync_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "account_company_sync/static/src/*/*.js",
            "account_company_sync/static/src/*/*.xml",
        ],
    },
    "installable": True,
}
