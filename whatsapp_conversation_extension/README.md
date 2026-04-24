# WhatsApp Conversation Extension

## Overview

This module extends the official Odoo 18.0 Enterprise **WhatsApp** module with:

- Conversation list menus (all / mine) in both the WhatsApp and Discuss apps.
- A security group to control who can see all conversations.
- A **Member Manager** role per WhatsApp account, with an "Edit Members" button in the conversation list and a minimal backend form to add/remove members.
- Custom `ir.rule` records that complement the restrictive base rules in the `mail` module, so that the new roles work correctly without requiring the users to be members of every channel they manage.

---

## Features

### 1. Conversation menus

Two new menus are added in **both** the WhatsApp and Discuss apps:

| Menu location | Item | Behaviour |
|---|---|---|
| WhatsApp → Conversations | All Conversations | Lists every WhatsApp channel in the system |
| WhatsApp → Conversations | My Conversations | Lists only channels where the current user is a member |
| Discuss → WhatsApp Conversations | All WhatsApp Conversations | Same as above, under Discuss |
| Discuss → WhatsApp Conversations | My WhatsApp Conversations | Same as above, under Discuss |

**"All Conversations"** menus and their action are restricted to the `View All WhatsApp Conversations` group.

### 2. Security groups

Both groups belong to the **Marketing / WhatsApp** category.

| XML ID | Name | Purpose |
|---|---|---|
| `group_whatsapp_view_all_conversations` | View All WhatsApp Conversations | Can open the "All Conversations" menus and read every WhatsApp channel and its members |
| `group_whatsapp_member_manager` | WhatsApp Channel Member Manager | Can add/remove members from WhatsApp channels for which the user is assigned as a manager |

### 3. Member Managers field on WhatsApp accounts

A new `Member Managers` Many2many field (`whatsapp_member_manager_ids`) is added to `whatsapp.account`. It is visible as a **Setting** block in the WhatsApp Business Account form, right after the *Notification Users* setting.

The field is filtered to show only users who already belong to the `group_whatsapp_member_manager` group.

### 4. "Edit Members" button in the conversation list

A button is injected into the official WhatsApp conversation list view (`whatsapp.discuss_channel_view_list_whatsapp`). The button is only visible to users who satisfy **both** conditions simultaneously:

1. Belong to `group_whatsapp_member_manager`.
2. Are listed in `wa_account_id.whatsapp_member_manager_ids` for that specific channel.

This double condition is evaluated by the computed field `can_manage_whatsapp_members` on `discuss.channel`.

Clicking the button opens a minimal backend form showing the conversation name, WhatsApp account, phone number, and an editable members list. An `AccessError` is raised server-side if the user does not meet both conditions.

---

## Technical details

### Extended models

#### `discuss.channel` (via `models/discuss_channel.py`)

| Added | Type | Description |
|---|---|---|
| `can_manage_whatsapp_members` | `Boolean` (computed) | `True` when the current user is in `group_whatsapp_member_manager` **and** listed in `wa_account_id.whatsapp_member_manager_ids` |
| `action_open_whatsapp_channel_form()` | method | Returns an `ir.actions.act_window` opening the minimal form; raises `AccessError` if the user is not authorised |

#### `whatsapp.account` (via `models/whatsapp_account.py`)

| Added | Type | Description |
|---|---|---|
| `whatsapp_member_manager_ids` | `Many2many → res.users` | Users who can manage members of conversations linked to this account |

### Security rules (`security/ir_rules.xml`)

The `mail` module ships restrictive `ir.rule` records that limit `discuss.channel` and `discuss.channel.member` visibility to channels where `is_member = True`. The module adds four complementary rules (all `noupdate="1"`):

| XML ID | Model | Group | Grants |
|---|---|---|---|
| `rule_discuss_channel_view_all_whatsapp` | `discuss.channel` | `group_whatsapp_view_all_conversations` | `perm_read` on all WhatsApp channels |
| `rule_discuss_channel_member_view_all_whatsapp` | `discuss.channel.member` | `group_whatsapp_view_all_conversations` | `perm_read` on members of all WhatsApp channels |
| `rule_discuss_channel_write_whatsapp_manager` | `discuss.channel` | `group_whatsapp_member_manager` | `perm_write` on WhatsApp channels |
| `rule_discuss_channel_member_manage_whatsapp` | `discuss.channel.member` | `group_whatsapp_member_manager` | `perm_read/write/create/unlink` on members of WhatsApp channels |

Because Odoo combines `ir.rule` records for the same model and group with **OR**, these rules override the restrictive base rules for users in the respective groups without affecting other users.

### Views (`views/`)

| File | View ID | Description |
|---|---|---|
| `whatsapp_conversation_menus.xml` | `whatsapp_conversation_all_action` | Window action — all WhatsApp channels |
| `whatsapp_conversation_menus.xml` | `whatsapp_conversation_my_action` | Window action — channels where `uid` is a member |
| `whatsapp_conversation_list_button.xml` | `discuss_channel_view_form_whatsapp_minimal` | Standalone minimal form for editing members |
| `whatsapp_conversation_list_button.xml` | `whatsapp_account_view_form_managers` | Inherits the WA account form; adds the Member Managers setting |
| `whatsapp_conversation_list_button.xml` | `discuss_channel_view_list_whatsapp_members_btn` | Inherits the WA conversation list; adds the Edit Members button |

---

## File structure

```
whatsapp_conversation_extension/
├── __init__.py
├── __manifest__.py
├── README.md
├── models/
│   ├── __init__.py
│   ├── discuss_channel.py       # can_manage_whatsapp_members + action
│   └── whatsapp_account.py      # whatsapp_member_manager_ids field
├── security/
│   ├── whatsapp_custom_groups.xml
│   ├── ir_rules.xml
│   └── ir.model.access.csv
└── views/
    ├── whatsapp_conversation_list_button.xml
    └── whatsapp_conversation_menus.xml
```

---

## Installation

1. Place the module in an addons path configured in `odoo.conf`.
2. The only explicit dependency is `whatsapp` (which in turn depends on `mail`).
3. Go to **Apps** → search for *WhatsApp Conversation Extension* → **Install**.

---

## Usage

### Viewing all conversations

1. Assign the user to the **View All WhatsApp Conversations** group.
2. Open **WhatsApp → Conversations → All Conversations** (or the equivalent under Discuss).

### Setting up a Member Manager

1. Assign the user to the **WhatsApp Channel Member Manager** group.
2. Open **WhatsApp → Configuration → WhatsApp Accounts** → edit the desired account.
3. In the **Member Managers** setting, add the user.
4. The user will now see the **Edit Members** button on all conversations linked to that account.

### Editing members

1. In any conversation list, click **Edit Members** (visible only to authorised managers).
2. Add or remove partners in the *Members* list on the minimal form.
3. Save.

---

## Dependencies

- `whatsapp` (Odoo 18.0 Enterprise — includes `mail` transitively)

## License

OEEL-1 (Odoo Enterprise Edition License v1)
