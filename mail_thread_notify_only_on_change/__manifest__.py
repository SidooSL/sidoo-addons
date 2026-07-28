###############################################################################
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
    "name": "Mail Thread Notify Only On Change",
    "version": "18.0.1.0.0",
    "category": "Technical",
    "summary": "Evita reenviar la notificación de asignación cuando user_id no cambia realmente",
    "description": """
        mail.thread reenvía el mensaje "You have been assigned to ..." en cada
        write() que incluya la clave user_id, sin comparar con el valor que ya
        tenía el registro. Cualquier integración externa que reescriba
        periódicamente el mismo responsable (por ejemplo, un conector que
        sincroniza datos y siempre incluye el comercial asignado en el
        payload) acaba inundando la bandeja de entrada del usuario con avisos
        duplicados.

        Este módulo corrige ese comportamiento a nivel de mail.thread: si
        user_id está en los valores de un write() pero coincide con el valor
        actual del registro, se omite el reenvío de la notificación de
        asignación para esos registros.
    """,
    "author": "Rialmar Aguilar, SDi",
    "license": "AGPL-3",
    "depends": ["mail"],
}
