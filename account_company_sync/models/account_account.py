from odoo import fields, models


class AccountAccount(models.Model):
    _inherit = "account.account"

    active = fields.Boolean(default=True)

    def _get_asset_field_name(self):
        """Determine which asset field to use based on installed modules"""
        if "asset_profile_id" in self._fields:
            return "asset_profile_id"  # OCA account_asset_management
        elif "asset_model" in self._fields:
            return "asset_model"  # Enterprise account_asset
        return None

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

    def find_target_record(self, field, target_company):
        if not self[field]:
            return False

        # Check if field exists in current model
        if field not in self._fields:
            return False

        model = self._fields[field].comodel_name
        if "ids" in field:
            if "company_id" in self.env[model]._fields:
                target_record = (
                    self.env[model]
                    .sudo()
                    .search(
                        [
                            ("name", "in", self[field].mapped("name")),
                            ("company_id", "=", target_company.id),
                        ]
                    )
                )
            else:
                target_record = self[field]
            return target_record.ids if target_record else False
        else:
            # Special handling for asset models that might have different search criteria
            if field in ("asset_profile_id", "asset_model"):
                domain = [("company_id", "=", target_company.id)]

                # For asset_profile_id (OCA), search by name
                if field == "asset_profile_id":
                    domain.append(("name", "=", self[field].name))
                # For asset_model (Enterprise), search by name and state=model
                elif field == "asset_model":
                    domain.extend(
                        [("name", "=", self[field].name), ("state", "=", "model")]
                    )

                target_record = self.env[model].sudo().search(domain, limit=1)
            else:
                target_record = (
                    self.env[model]
                    .sudo()
                    .search(
                        [
                            ("name", "=", self[field].name),
                            ("company_id", "=", target_company.id),
                        ],
                        limit=1,
                    )
                )
        return target_record.id if target_record else False

    def compare_and_update_fields(self, target_account):
        fields_to_sync = {
            "name": self.name,
            "account_type": self.account_type,
            "reconcile": self.reconcile,
            "deprecated": self.deprecated,
            "centralized": self.centralized,
            "currency_id": self.currency_id.id,
            "group_id": self.find_target_record("group_id", target_account.company_id),
            "tax_ids": self.find_target_record("tax_ids", target_account.company_id),
            "tag_ids": self.find_target_record("tag_ids", target_account.company_id),
            "allowed_journal_ids": self.find_target_record(
                "allowed_journal_ids", target_account.company_id
            ),
        }

        # Add asset field based on available module
        asset_field = self._get_asset_field_name()
        if asset_field:
            fields_to_sync[asset_field] = self.find_target_record(
                asset_field, target_account.company_id
            )

        updates = {}
        for field, value in fields_to_sync.items():
            if isinstance(self._fields[field], fields.Many2one):
                if target_account[field].id != value:
                    updates[field] = value
            elif isinstance(self._fields[field], fields.Many2many):
                updates[field] = [(6, 0, value)] if value else [(6, 0, [])]
            else:
                if target_account[field] != value:
                    updates[field] = value

        if updates:
            target_account.sudo().write(updates)

    def search_account_and_duplicate(self, company_id):
        account = self.sudo().search(
            [
                ("company_id", "=", company_id.id),
                ("code", "=", self.code),
                ("active", "in", [True, False]),
            ],
            limit=1,
        )
        if not account:
            copy_vals = {
                "company_id": company_id.id,
                "code": self.code,
                "name": self.name,
                "group_id": self.find_target_record("group_id", company_id),
                "tax_ids": self.find_target_record("tax_ids", company_id),
                "tag_ids": self.find_target_record("tag_ids", company_id),
                "allowed_journal_ids": self.find_target_record(
                    "allowed_journal_ids", company_id
                ),
            }

            # Add asset field based on available module
            asset_field = self._get_asset_field_name()
            if asset_field:
                copy_vals[asset_field] = self.find_target_record(
                    asset_field, company_id
                )

            account = self.sudo().copy(copy_vals)
        else:
            self.compare_and_update_fields(account)

    def create_account_in_companies(self, company_ids=None):
        for record in self:
            companies = company_ids or record.get_company_to_sync()
            for company in companies:
                record.search_account_and_duplicate(company)

    def sync_accounts_across_companies(self):
        companies = self.env["res.company"].search(
            [
                ("parent_id", "=", False),
            ]
        )
        accounts_by_company = {}

        for company in companies:
            accounts_by_company[company.id] = self.search(
                [("company_id", "=", company.id), ("active", "in", [True, False])]
            )

        for company_id, accounts in accounts_by_company.items():
            for account in accounts:
                for target_company in companies:
                    if target_company.id != company_id:
                        account.search_account_and_duplicate(target_company)

    def enqueue_sync_accounts_across_companies(self):
        self.with_delay().sync_accounts_across_companies()
