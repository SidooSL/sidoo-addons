{
    "name": "WhatsApp Conversation Extension",
    "version": "1.0",
    "category": "Marketing/WhatsApp",
    "summary": "Adds advanced conversation management menus for WhatsApp",
    "description": """
        This module extends the official Odoo WhatsApp module by providing:
        - A new menu 'WhatsApp Conversations' under the WhatsApp module
        - Submenu 'All WhatsApp Conversations': view all conversations in the system
        - Submenu 'My WhatsApp Conversations': view only conversations where the current user is a member

        The module leverages the existing discuss.channel model and reuses existing views,
        without duplicating any logic from the official WhatsApp module.
    """,
    "authors": [
        "Mario Villaescusa (mvillaescusa@sdi.es)",
        "Susana Romero (sromero@sdi.es)",
        "SDi",
    ],
    "depends": ["whatsapp"],
    "data": [
        "security/whatsapp_custom_groups.xml",
        "security/ir_rules.xml",
        "security/ir.model.access.csv",
        "views/whatsapp_conversation_list_button.xml",
        "views/whatsapp_conversation_menus.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
    "external_dependencies": {},
    "license": "OEEL-1",
}
