###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
import base64

import xlrd

from odoo import Command, fields, models


class WizardImportProductVariant(models.TransientModel):
    _name = "wizard.import.product.variant"
    _description = "Wizard to import product variants"

    excel_file = fields.Binary(
        help="Excel file with products, variants and stock information",
    )

    import_stock = fields.Boolean(default=False)

    import_stock_without_qty = fields.Boolean(default=False)

    def format_supplier_name(self, name):
        if "/" in name.value:
            # Roly / Gorfactory
            return name.value.split("/")[1]
        return name.value

    def create_variant_attribute_dict(self, variant_data, col_name):
        variant_dict = {}
        for row in range(1, variant_data.nrows):
            data = variant_data.row(row)
            code = data[0].value
            variant_name = data[1].value

            if code not in variant_dict:
                variant_dict[code] = {}

            if variant_name not in variant_dict[code]:
                variant_dict[code][variant_name] = {}

            # add variant attribute
            for attribute in range(2, len(col_name)):
                variant_dict[code][variant_name][col_name[attribute].value] = data[
                    attribute
                ].value

        return variant_dict

    def import_excel_products(self):
        file_content = base64.decodebytes(self.excel_file)
        wb = xlrd.open_workbook(file_contents=file_content)
        ws_product = wb.sheet_by_index(0)  # fist sheet with product info
        ws_variant = wb.sheet_by_index(1)  # second sheet with variant info
        ws_stock = wb.sheet_by_index(2)  # third sheet with variant info
        variant_col_name = ws_variant.row(0)

        # create variant dict
        variant_dict = self.create_variant_attribute_dict(ws_variant, variant_col_name)

        # create product
        for row in range(1, ws_product.nrows):
            data = ws_product.row(row)
            default_code = data[0]
            product_id = self.env["product.product"].search(
                [("default_code", "=", default_code.value)]
            )
            if not product_id and default_code.value != "":
                values = self.prepare_product_variant_values(data)
                values = self.prepare_product_variant_attributes(
                    variant_dict, default_code, values
                )
                product_id = self.env["product.template"].create(values)
                self.create_product_supplier(product_id, data)

                if self.import_stock:
                    self.import_product_variant_stock(ws_stock, product_id)

    def create_product_supplier(self, product_id, data):
        supplier_name = self.format_supplier_name(data[3])
        if supplier_name and supplier_name != "":
            supplier_id = self.env["res.partner"].search(
                [("name", "like", supplier_name)]
            )
            if not supplier_id:
                supplier_id = self.env["res.partner"].create(
                    {
                        "name": supplier_name,
                        "company_type": "company",
                    }
                )
            if supplier_id:
                price = data[2]
                self.env["product.supplierinfo"].create(
                    {
                        "partner_id": supplier_id.id,
                        "min_qty": 1.0,
                        "delay": 0,
                        "price": price.value,
                        "product_tmpl_id": product_id.id,
                        "currency_id": self.env.company.currency_id.id,
                    }
                )

    def create_product_tag(self, data):
        # Tag and Product
        tag_ids = False
        tag_name = data[4]
        if tag_name.value != "":
            product_tag_id = self.env["product.tag"].search(
                [("name", "=", tag_name.value)]
            )
            if not product_tag_id:
                product_tag_id = self.env["product.tag"].create(
                    {"name": tag_name.value}
                )
            tag_ids = [Command.link(product_tag_id.id)]
        return tag_ids

    def prepare_product_variant_attributes(self, variant_dict, code, values):
        if code.value not in variant_dict:
            return values

        variant_data = variant_dict[code.value]

        for data in variant_data.keys():
            variant_values = variant_data[data]
            product_attribute_id = self.env["product.attribute"].search(
                [("name", "=", data)]
            )
            if not product_attribute_id:
                product_attribute_id = self.env["product.attribute"].create(
                    {"name": data}
                )
            selected_attribute_values = []
            for value in variant_values.values():
                product_attribute_value = self.env["product.attribute.value"].search(
                    [
                        ("name", "=", value),
                        ("attribute_id", "=", product_attribute_id.id),
                    ]
                )
                if not product_attribute_value:
                    product_attribute_value = self.env[
                        "product.attribute.value"
                    ].create(
                        {
                            "name": value,
                            "attribute_id": product_attribute_id.id,
                        }
                    )
                selected_attribute_values.append(product_attribute_value.id)

            if "attribute_line_ids" not in values:
                values["attribute_line_ids"] = []

            values["attribute_line_ids"].append(
                Command.create(
                    {
                        "attribute_id": product_attribute_id.id,
                        "value_ids": [Command.set(selected_attribute_values)],
                    }
                ),
            )
        return values

    def prepare_product_variant_values(self, data):
        product_values = {}
        name = data[1]
        standard_price = data[2]

        tag_ids = self.create_product_tag(data)

        product_values.update(
            {
                "name": name.value,
                "detailed_type": "product",
                "invoice_policy": "delivery",
                "standard_price": standard_price.value,
                "product_tag_ids": tag_ids,
            }
        )
        return product_values

    def import_product_variant_stock(self, stock_data, product_id):
        for row in range(1, stock_data.nrows):
            data = stock_data.row(row)
            code = data[0].value
            attributes = code.split("-")[1:]
            quantity = data[1].value
            variant_amount = data[2].value
            attribute_values_ids = self.env["product.template.attribute.value"].search(
                [
                    ("name", "in", attributes),
                    ("product_tmpl_id", "=", product_id.id),
                ]
            )
            variant_id = False
            if attribute_values_ids:
                variant_id = product_id.product_variant_ids.filtered(
                    lambda x, attribute_values_ids=attribute_values_ids: (
                        x.product_template_attribute_value_ids.ids
                        == attribute_values_ids.ids
                    )
                )
            if variant_id:
                variant_id.write(
                    {
                        "standard_price": variant_amount,
                        "default_code": code,
                    }
                )
                if not self.import_stock_without_qty:
                    location_id = self.env.ref("stock.stock_location_stock")
                    quant = self.env["stock.quant"].create(
                        {
                            "location_id": location_id.id,
                            "product_id": variant_id.id,
                            "inventory_quantity": quantity,
                        }
                    )
                    quant.action_apply_inventory()
