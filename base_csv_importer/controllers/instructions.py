import os

from odoo import http
from odoo.http import request


class AccountImporterController(http.Controller):
    @http.route("/base_csv_importer/download_instructions", type="http", auth="user")
    def download_instructions(self):
        # Ruta del archivo ZIP dentro del módulo
        module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        zip_path = os.path.join(module_path, "static", "docs", "instrucciones.zip")

        if not os.path.exists(zip_path):
            return request.not_found()

        # Abrir y leer el archivo ZIP
        with open(zip_path, "rb") as f:
            zip_data = f.read()

        # Configurar la respuesta HTTP para la descarga
        return request.make_response(
            zip_data,
            headers=[
                ("Content-Type", "application/zip"),
                (
                    "Content-Disposition",
                    'attachment; filename="instrucciones_importador.zip"',
                ),
                ("Content-Length", str(len(zip_data))),
            ],
        )
