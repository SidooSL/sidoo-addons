{
    "name": "Mail SDI Full Composer",
    "version": "18.0.1.0.0",
    "category": "Discuss",
    "summary": "Abre el compositor completo desde Enviar Mensaje en el chatter",
    "description": """
        Sustituye el comportamiento del boton Enviar Mensaje del chatter para
        abrir directamente el compositor completo de correo.
    """,
    "author": "SDi",
    "license": "LGPL-3",
    "depends": ["mail"],
    "assets": {
        "web.assets_backend": [
            "mail_sdi_full_composer/static/src/js/chatter_full_composer.esm.js",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": False,
}
