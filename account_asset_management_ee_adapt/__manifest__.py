{
    "name": "Account Asset Management EE Adapt",
    "version": "16.0.1.0.0",
    "summary": """
    Adaptation of the account_asset_management menu for the EE accounting
     version.""",
    "author": "Oscar Soto, Sidoo SL",
    "maintainer": "Sidoo SL",
    "website": "https://sidoo.es",
    "license": "AGPL-3",
    "excludes": ["account_asset"],
    "depends": [
        "account_asset_management",
        "account_accountant",
    ],
    "data": [
        "views/menuitem.xml",
    ],
}
