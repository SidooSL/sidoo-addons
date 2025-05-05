=================================
Account Asset Initiated Assistant
=================================

This module enhances the asset management functionality in Odoo by providing:

Features
--------

* New view for Account Asset Lines
* Quick access to asset lines from the asset form
* Ability to mark depreciation lines as initialized

Key Functionalities
-------------------

1. Asset Lines Overview
~~~~~~~~~~~~~~~~~~~~~~

* Adds a new tree view for Account Asset Lines
* Displays detailed information about each asset line

2. Asset Form Enhancement
~~~~~~~~~~~~~~~~~~~~~~~~

* Adds a smart button on the asset form to quickly access related asset lines
* Provides a direct link to view all lines associated with a specific asset

3. Batch Initialization
~~~~~~~~~~~~~~~~~~~~~~

* Includes a server action to mark multiple asset lines as initialized
* Allows bulk updating of the 'init_entry' field for selected lines

Requirements
------------

* Odoo 17.0
* account_asset_management module
