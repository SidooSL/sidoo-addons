# Account Report Prefooter Text

## Overview

This module adds configurable HTML text fields that appear before the company footer in invoice PDF reports, with separate content for customer invoices and vendor bills.

**Version**: 18.0.1.0.0
**Category**: Accounting/Accounting
**License**: LGPL-3

## Purpose

Enables companies to display custom HTML content before the footer section in invoice PDFs, with different content based on whether it's a customer document or a vendor document.

## Use Cases

- Display custom legal disclaimers specific to customer invoices
- Add vendor-specific payment instructions on vendor bills
- Show different regulatory information for incoming vs outgoing invoices
- Display multi-line formatted text with proper styling

## Configuration

### Installation

Install the module through Odoo Apps menu.

### Setup

After installing, configure the footer texts in:

**Accounting > Configuration > Settings**

Navigate to the **Invoicing Settings** section where you will find:

1. **Customer Invoice Footer Text**
   - Appears before footer in customer invoices and credit notes
   - Supports full HTML formatting
   - Translatable for multi-language environments
   - Placeholder: "Enter HTML text to display before footer in customer invoices..."

2. **Vendor Bill Footer Text**
   - Appears before footer in vendor bills and refunds
   - Supports full HTML formatting
   - Translatable for multi-language environments
   - Placeholder: "Enter HTML text to display before footer in vendor bills..."

### Paper Format Configuration

> **⚠️ Important Recommendation**: If you add multi-line content in the footer texts, it's recommended to increase the **bottom margin** of your A4 paper format to prevent content overlap or truncation.

To adjust the paper format:

1. Navigate to **Settings > Technical > Reporting > Paper Format**
2. Open the **A4** format (or your default paper format)
3. Increase the **Bottom Margin (mm)** field
   - Default: 15mm
   - Recommended with footer text: 25-35mm (depending on content length)
4. Save the changes

This ensures that the custom footer text has adequate space to prevent it from displacing the rest of the company footer content and being cut off in the PDF.

## Features

- ✅ Separate configurable text for customer invoices and vendor bills
- ✅ Full HTML support for rich text formatting
- ✅ Multi-language support (translatable fields)
- ✅ Automatically displayed based on invoice type
- ✅ Compatible with all three Odoo report layouts:
  - Standard layout
  - Boxed layout
  - Bubble layout
- ✅ Only displays when content is not empty
- ✅ Centered text with muted styling by default
- ✅ Per-company configuration (multi-company compatible)

## Technical Details

### Dependencies

- `account`: Core accounting module
- `web`: Web interface module


### Invoice Types Supported

| Invoice Type | Field Used | Document Types |
|-------------|------------|----------------|
| Customer Invoice Footer Text | `customer_invoice_footer_text` | `out_invoice`, `out_refund` |
| Vendor Bill Footer Text | `vendor_bill_footer_text` | `in_invoice`, `in_refund` |

### Report Templates Inherited

The module inherits three external layout templates to ensure compatibility with all report layouts:

1. **`web.external_layout_standard`** - Standard layout template
2. **`web.external_layout_boxed`** - Boxed layout template
3. **`web.external_layout_bubble`** - Bubble layout template

Each template adds the custom footer text before the company `report_footer` field using XPath expressions.
