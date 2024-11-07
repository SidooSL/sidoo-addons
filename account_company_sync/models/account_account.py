from odoo import models


class AccountAccount(models.Model):
    _inherit = "account.account"

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

    def create_account_in_companies(self, company_ids=None):
        for record in self:
            companies = company_ids or record.get_company_to_sync()
            for company in companies:
                account = (
                    self.env["account.account"]
                    .sudo()
                    .search(
                        [
                            ("company_id", "=", company.id),
                            ("code", "=", record.code),
                        ],
                        limit=1,
                    )
                )
                if not account:
                    record.sudo().copy(
                        {
                            "company_id": company.id,
                            "code": record.code,
                            "name": record.name,
                        }
                    )
