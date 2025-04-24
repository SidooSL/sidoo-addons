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
    "name": "Importador contable",
    "summary": "Herramienta para importar datos contables en Odoo",
    "author": "Fernando La Chica, Sidoo Soluciones, S.L.",
    "website": "https://sidoo.es/",
    "license": "AGPL-3",
    "category": "Accounting",
    "version": "17.0.1.0.0",
    "depends": [
        "base_csv_importer",
    ],
    "data": [
        "data/ai_template_file_map_bank_account.xml",
        "data/ai_template_file_map_account_move.xml",
        "data/ai_template_file_map_payment.xml",
        "data/ai_template_file_map_invoice.xml",
        "data/ai_template_file_records.xml",
    ],
    "application": True,
}
