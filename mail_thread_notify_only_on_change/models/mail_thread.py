from odoo import models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def write(self, values):
        user_id = values.get("user_id")
        field = self._fields.get("user_id")
        if not user_id or not field or field.comodel_name != "res.users":
            return super().write(values)

        unchanged = self.filtered(lambda rec: rec.user_id.id == user_id)
        if not unchanged:
            return super().write(values)

        changed = self - unchanged
        result = True
        if changed:
            result = super(MailThread, changed).write(values) and result
        rest = {key: val for key, val in values.items() if key != "user_id"}
        if rest:
            result = super(MailThread, unchanged).write(rest) and result
        return result
