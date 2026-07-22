from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPartnerTierValidationAuto(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.approver = cls.env["res.users"].create(
            {
                "name": "Contact approver",
                "login": "contact-approver",
                "groups_id": cls.env.ref("base.group_user").ids,
            }
        )
        stages = cls.env["res.partner.stage"]
        stages.search([("is_default", "=", True)]).is_default = False
        cls.draft_stage = stages.search([("state", "=", "draft")], limit=1)
        cls.draft_stage.is_default = True
        cls.approved_stage = stages.search([("state", "=", "confirmed")], limit=1)
        cls.env["tier.definition"].create(
            {
                "name": "Approve companies automatically",
                "model_id": cls.env.ref("base.model_res_partner").id,
                "review_type": "individual",
                "reviewer_id": cls.approver.id,
                "definition_domain": "[('is_company', '=', True)]",
            }
        )

    def test_creation_requests_validation_and_archives_partner(self):
        partner = self.env["res.partner"].create(
            {"name": "Company pending approval", "is_company": True}
        )

        self.assertFalse(partner.active)
        self.assertEqual(partner.state, "draft")
        self.assertEqual(partner.validation_status, "pending")
        self.assertTrue(partner.review_ids)

        with self.assertRaises(ValidationError):
            partner.active = True

        partner.with_user(self.approver).validate_tier()

        self.assertTrue(partner.active)
        self.assertEqual(partner.stage_id, self.approved_stage)
        self.assertEqual(partner.validation_status, "validated")

    def test_partner_without_applicable_rule_is_not_archived(self):
        partner = self.env["res.partner"].create(
            {"name": "Person without approval", "is_company": False}
        )

        self.assertTrue(partner.active)
        self.assertFalse(partner.review_ids)

    def test_sensitive_change_restarts_validation(self):
        partner = self.env["res.partner"].create(
            {"name": "Approved company", "is_company": True}
        )
        partner.with_user(self.approver).validate_tier()

        partner.write({"vat": "ES12345678Z"})

        self.assertFalse(partner.active)
        self.assertEqual(partner.state, "draft")
        self.assertEqual(partner.validation_status, "pending")
        self.assertTrue(partner.review_ids)
