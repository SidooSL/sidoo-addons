###############################################################################
#
#    Sidoo Soluciones, S.L.
#    Copyright (C) 2024-Today Sidoo Soluciones, S.L. <www.sidoo.es>
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
    'name': 'Partner Industry Edit Group',
    'summary': 'Add a group to CRUD the partner industry, not only the admin',
    'author': 'Jorge Quinteros, Sidoo Soluciones, S.L.',
    'website': 'https://sidoo.es/',
    'license': 'AGPL-3',
    'category': 'Tools',
    'version': '16.0.1.0.1',
    'depends': [
        'base',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/res_partner_industry_views.xml',
    ],
}
