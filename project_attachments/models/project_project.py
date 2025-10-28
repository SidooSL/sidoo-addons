from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    attachment_count = fields.Integer(
        string="Attachments", compute="_compute_attachment_count"
    )

    @api.depends("task_ids")
    def _compute_attachment_count(self):
        for project in self:
            # Get task IDs for this project
            task_ids = project.task_ids.ids

            # Build domain to search attachments for project and its tasks
            domain = [
                "|",
                "&",
                ("res_model", "=", "project.project"),
                ("res_id", "=", project.id),
                "&",
                ("res_model", "=", "project.task"),
                ("res_id", "in", task_ids),
            ]

            project.attachment_count = self.env["ir.attachment"].search_count(domain)

    def action_view_attachments(self):
        task_ids = self.task_ids.ids

        # Domain to filter attachments for this project and its tasks
        domain = [
            "|",
            "&",
            ("res_model", "=", "project.project"),
            ("res_id", "=", self.id),
            "&",
            ("res_model", "=", "project.task"),
            ("res_id", "in", task_ids),
        ]

        return {
            "name": f"Attachments - {self.name}",
            "type": "ir.actions.act_window",
            "res_model": "ir.attachment",
            "view_mode": "kanban,list,form",
            "domain": domain,
            "context": {
                "default_res_model": "project.project",
                "default_res_id": self.id,
            },
            "target": "current",
        }
