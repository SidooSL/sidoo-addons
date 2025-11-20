###############################################################################
#
#    Sidoo Soluciones, S.L.
#    Copyright (C) 2025-Today Sidoo Soluciones, S.L. <www.sidoo.es>
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
    "name": "Base CSV Importer",
    "summary": "Herramienta para importar ficheros csv en Odoo",
    "author": "Fernando La Chica, Sidoo Soluciones, S.L.",
    "website": "https://sidoo.es/",
    "license": "AGPL-3",
    "category": "Accounting",
    "version": "18.0.1.0.0",
    "depends": [
        "base",
        "queue_job",
        "product",
        "sale_management",
        "account",
    ],
    "application": True,
    "data": [
        "data/ai_template_type.xml",
        "data/maps/ai_template_file_map_contact.xml",
        "data/maps/ai_template_file_map_category.xml",
        "data/maps/ai_template_file_map_product_template.xml",
        "data/ai_template_file_records.xml",
        "data/ir_cron.xml",
        "security/ir.model.access.csv",
        "data/ai_action_server.xml",
        "views/menu_views.xml",
        "views/ai_record_views.xml",
        "views/ai_import_type_views.xml",
        "views/ai_file_bundle_views.xml",
        "views/ai_file_views.xml",
        "views/ai_template_file_views.xml",
        "views/ai_template_file_map_views.xml",
        "views/ai_error_views.xml",
        "views/ai_record_batch_views.xml",
    ],
}
