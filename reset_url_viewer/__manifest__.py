################################################################################
#
#    SDi
#    Copyright (C) 2026 SDi <www.sdi.es>
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
    'name': 'Reset Password URL Viewer',
    'version': '18.0.1.0.0',
    'summary': 'Generate and display password reset URL without sending email',
    'description': """
        Module for neutralized or testing environments.
        It generates the password reset link
        and displays it in a wizard with a copy-to-clipboard button,
        without sending any email.
    """,
    'category': 'Technical',
    'author': 'Rialmar Aguilar, SDi',
    'depends': ['base', 'auth_signup'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_config_parameter_data.xml',
        'wizard/reset_url_wizard_views.xml',
        'views/res_users_action.xml',
    ],
    'license': 'AGPL-3',
}
