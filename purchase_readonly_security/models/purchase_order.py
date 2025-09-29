###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from lxml import etree

from odoo import _, api, models
from odoo.exceptions import AccessError
from odoo.tools import config


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        result = super().get_view(view_id=view_id, view_type=view_type, **options)
        group = "purchase_readonly_security.group_purchase_readonly_security_admin"
        if view_type == "form" and not self.env.user.has_group(group):
            doc = etree.XML(result["arch"])
            for node in doc.xpath("//header"):
                node.set("invisible", "1")
            result["arch"] = etree.tostring(doc, encoding="unicode")
        return result

    @api.model
    def check_access(self, operation):
        """Simulate that you do not have ACLs so that the create, edit, and delete
        buttons are not displayed.
        """
        user = self.env.user
        group = "purchase_readonly_security.group_purchase_readonly_security_admin"
        test_condition = not config["test_enable"] or (
            config["test_enable"]
            and self.env.context.get("test_purchase_readonly_security")
        )
        if (
            test_condition
            and operation != "read"
            and not self.env.su
            and not user.has_group(group)
        ):
            raise AccessError(
                _(
                    "Sorry, you are not allowed to create/edit purchase orders. "
                    "Please contact your administrator for further information."
                )
            )

        return super().check_access(operation=operation)

    def has_access(self, operation):
        """Return whether the current user is allowed to perform operation on purchase orders."""
        user = self.env.user
        group = "purchase_readonly_security.group_purchase_readonly_security_admin"
        test_condition = not config["test_enable"] or (
            config["test_enable"]
            and self.env.context.get("test_purchase_readonly_security")
        )
        if (
            test_condition
            and operation != "read"
            and not self.env.su
            and not user.has_group(group)
        ):
            return False
        return super().has_access(operation)

    def _create_invoices(self, grouped=False, final=False, date=None):
        """Check if the user can do it, the method does not do a write() in purchase.order,
        the computes set the corresponding values with compute methods.
        Apply the following logic: If user cannot modify a purchase.order, cannot create
        an invoice.
        """
        self.env["purchase.order"].check_access("write")
        return super()._create_invoices(grouped=grouped, final=final, date=date)
