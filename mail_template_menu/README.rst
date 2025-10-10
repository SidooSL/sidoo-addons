====================
Mail Template Menu
====================

Purpose
=======

This module adds a dedicated menu item for "Mail Templates" under the Discuss application. This provides quick and easy access for users who need to manage email templates frequently, without having to navigate through the general settings menu.

Use Cases
=========

- **System Administrators**: Quickly access and manage all system and module-related email templates.
- **Marketing Teams**: Easily create, edit, and organize templates for email campaigns.
- **Developers**: A direct entry point to view and debug mail templates during development.

Features
========

- Adds a "Mail Templates" menu item directly within the "Discuss" application.
- The menu is only visible to users belonging to the "Mail Template Editor" group (``mail.group_mail_template_editor``), ensuring proper access control.
- Provides direct access to the list and form views of ``mail.template``.

Configuration
=============

No special configuration is needed. After installation, the menu will be available to users with the appropriate permissions.

Required Permissions
--------------------

To see the menu, users must be part of the following group:

- **Access Group**: ``mail.group_mail_template_editor``

This group is specifically required for editing email templates that contain dynamic placeholders (e.g., for QWeb expressions), as this can involve executing code.

Installation
============

To install this module, you need to:

1. Add it to your custom addons path.
2. Restart the Odoo server.
3. Go to **Apps**, search for "Mail Templates Menu", and click **Install**.

License
=======

LGPL-3
