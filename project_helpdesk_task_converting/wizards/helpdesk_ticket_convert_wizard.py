from odoo import models


class HelpdeskTicketConvertWizard(models.TransientModel):
    _inherit = "helpdesk.ticket.convert.wizard"

    def _default_project_id(self):
        if self.env.context.get("to_convert"):
            ticket = self.env["helpdesk.ticket"].browse(
                self.env.context["to_convert"][0]
            )
            if ticket.partner_id and ticket.partner_id.project_ids:
                return ticket.partner_id.project_ids[0].id
        return super()._default_project_id()

    def action_convert(self):
        result = super().action_convert()
        tickets_to_convert = self._get_tickets_to_convert()

        tasks = self.env["project.task"].search(
            [
                ("project_id", "=", self.project_id.id),
                ("name", "in", tickets_to_convert.mapped("name")),
            ]
        )

        for ticket, task in zip(tickets_to_convert, tasks, strict=True):
            analytic_lines = self.env["account.analytic.line"].search(
                [("helpdesk_ticket_id", "=", ticket.id)]
            )
            if analytic_lines:
                analytic_lines.write(
                    {
                        "helpdesk_ticket_id": False,
                        "task_id": task.id,
                    }
                )

        return result
