import json

from odoo import models


class ReSequenceWizard(models.TransientModel):
    _inherit = "account.resequence.wizard"

    def resequence(self):
        # Override to fix problem with sequence constraint when migrate db with openupgrade
        new_values = json.loads(self.new_values)
        moves_to_rename = self.env["account.move"].browse(
            int(k) for k in new_values.keys()
        )
        for move in moves_to_rename:
            move.name = move.name + "/"

        moves_to_rename.flush_recordset(["name"])
        # If the db is not forcibly updated, the temporary renaming could only happen in cache and still trigger the constraint

        for move_id in self.move_ids:
            if str(move_id.id) in new_values:
                if self.ordering == "keep":
                    move_id.name = new_values[str(move_id.id)]["new_by_name"]
                else:
                    move_id.name = new_values[str(move_id.id)]["new_by_date"]
