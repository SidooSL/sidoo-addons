from odoo import fields, models


class AccountAccount(models.Model):
    _inherit = "account.account"

    active = fields.Boolean(default=True)

    def get_company_to_sync(self):
        return (
            self.env["res.company"]
            .sudo()
            .search(
                [
                    ("id", "!=", self.company_id.id),
                ]
            )
        )

    def search_account_and_duplicate(self, company_id):
        account = self.sudo().search(
            [
                ("company_id", "=", company_id),
                ("code", "=", self.code),
            ],
            limit=1,
        )
        if not account:
            account = self.sudo().copy(
                {"company_id": company_id, "code": self.code, "name": self.name}
            )

    def create_account_in_companies(self, company_ids=None):
        for record in self:
            companies = company_ids or record.get_company_to_sync()
            for company in companies:
                record.search_account_and_duplicate(company.id)

    def sync_accounts_across_companies(self):
        companies = self.env["res.company"].search(
            [
                ("parent_id", "=", False),
            ]
        )
        accounts_by_company = {}

        for company in companies:
            accounts_by_company[company.id] = self.search(
                [("company_id", "=", company.id)]
            )

        for company_id, accounts in accounts_by_company.items():
            for account in accounts:
                for target_company in companies:
                    if target_company.id != company_id:
                        account.search_account_and_duplicate(target_company.id)

    def enqueue_sync_accounts_across_companies(self):
        self.with_delay().sync_accounts_across_companies()
