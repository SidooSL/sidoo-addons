from odoo import _, api, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"
    _description = "Journal Entry"

    @api.model_create_multi
    def create(self, vals_list):
        # Si la plantilla no tiene marcado el check de recalcular, no se crean las líneas nuevas de impuestos
        if self._context.get("no_recalculate", False):
            if any(
                "state" in vals and vals.get("state") == "posted" for vals in vals_list
            ):
                raise UserError(
                    _(
                        "You cannot create a move already in the posted state. Please create a draft move and post it after."
                    )
                )
            container = {"records": self}
            with self._check_balanced(container):
                with self._sync_dynamic_lines(container):
                    for vals in vals_list:
                        self._sanitize_vals(vals)
                    moves = super().create(vals_list)
                for move, vals in zip(moves, vals_list):
                    if "tax_totals" in vals:
                        move.tax_totals = vals["tax_totals"]
            return moves
        return super().create(vals_list)
