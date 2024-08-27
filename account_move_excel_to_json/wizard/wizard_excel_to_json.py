import base64
import io
import json

import pandas as pd

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class WizardExcelToJson(models.TransientModel):
    _name = "wizard.excel.to.json"
    _description = "Wizard to convert Excel to JSON"

    excel_file = fields.Binary(required=True)
    json_result = fields.Text(readonly=True)

    def open_account_move_template_wizard(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move.template.run",
            "view_mode": "form",
            "target": "new",
            "context": {"default_overwrite": self.json_result},
        }

    def convert_excel_to_json(self):
        # Read Excel
        file_content = base64.b64decode(self.excel_file)
        excel_data = pd.read_excel(io.BytesIO(file_content))

        #  Take care NaN values
        if "Importe" in excel_data.columns:
            excel_data["Importe"] = excel_data["Importe"].fillna(0)

        # Create dictionary
        result = {}
        for index, row in excel_data.iterrows():
            if "Importe" in row:
                amount = row["Importe"]
            else:
                raise ValidationError(
                    _('The Excel file must have a column named "Amount"')
                )
            key = f"L{index + 1}"
            result[key] = {"amount": amount}

        # Convert to JSON
        json_result = json.dumps(result, indent=4)

        # Save result
        self.json_result = json_result

        return {
            "type": "ir.actions.act_window",
            "res_model": "wizard.excel.to.json",
            "view_mode": "form",
            "res_id": self.id,
            "target": "new",
        }
