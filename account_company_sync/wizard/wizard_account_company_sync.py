from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class WizardAccountCompanySync(models.TransientModel):
    _name = "wizard.account.company.sync"
    _description = "Wizard to sync account in companies"

    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)

    account_ids = fields.Many2many("account.account")

    company_ids = fields.Many2many(
        "res.company",
        string="Companies",
        domain=lambda self: [
            ("id", "!=", self.env.company.id),
            ("id", "in", self.env.user.company_ids.ids),
        ],
        readonly=False,
        compute="_compute_companies",
    )

    @api.depends("company_id")
    def _compute_companies(self):
        for record in self:
            record.company_ids = (
                self.env["res.company"]
                .sudo()
                .search(
                    [
                        ("id", "!=", record.company_id.id),
                        ("id", "in", self.env.user.company_ids.ids),
                    ]
                )
            )

    def action_sync_account(self):
        for record in self:
            if not record.account_ids:
                raise ValidationError(_("Please select accounts to sync."))
            record.account_ids.create_account_in_companies(record.company_ids)
        return {"type": "ir.actions.act_window_close"}
