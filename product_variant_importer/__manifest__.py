###############################################################################
#
#    SDi Digital Group
#    Copyright (C) 2024-Today SDi Digital Group https://www.sdi.es/odoo-cloud/
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
{
    "name": "Product Variant Importer",
    "version": "16.0.1.0.0",
    "summary": "Product Variant Importer",
    "author": "Luis Adan Jimenez Hernandez, Sidoo Soluciones S.L.",
    "website": "https://sidoo.es",
    "license": "AGPL-3",
    "category": "Custom",
    "depends": ["base", "stock"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/wizard_import_product_variant.xml",
    ],
    "application": True,
}
