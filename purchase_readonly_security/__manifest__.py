###############################################################################
#
#    SDi
#    Copyright (C) 2025-Today SDi <www.sidoo.es>
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
    "name": "Purchase Readonly Security",
    "summary": "Creates a specific permission to allow modification of purchase orders",
    "version": "18.0.1.0.0",
    "category": "Custom",
    "website": "https://www.sdi.es/tecnologias/odoo/",
    "author": "Jorge Quinteros, SDi",
    "license": "AGPL-3",
    "depends": ["purchase"],
    "data": [
        "security/purchase_readonly_security.xml",
    ],
}
