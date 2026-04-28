/** @odoo-module **/

import { Chatter } from "@mail/chatter/web_portal/chatter";
import { prettifyMessageContent } from "@mail/utils/common/format";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";

patch(Chatter.prototype, {
    setup() {
        super.setup(...arguments);
        this.action = useService("action");
    },

    async _openMessageFullComposer() {
        const thread = this.state.thread;
        const composer = thread.composer;
        const attachments = composer.attachments || [];
        const suggestedRecipients = thread.suggestedRecipients || [];
        const body = composer.text || "";
        const validMentions = this.store.getMentionsFromText(body, {
            mentionedChannels: composer.mentionedChannels,
            mentionedPartners: composer.mentionedPartners,
        });
        let defaultBody = await prettifyMessageContent(body, validMentions);
        if (!defaultBody) {
            defaultBody = "";
        }
        if (composer.emailAddSignature && thread.effectiveSelf?.signature) {
            defaultBody = `${defaultBody}<br>${thread.effectiveSelf.signature}`;
        }
        const context = {
            default_attachment_ids: attachments.map((attachment) => attachment.id),
            default_body: `<div>${defaultBody}</div>`,
            default_email_add_signature: false,
            default_model: thread.model,
            default_partner_ids: suggestedRecipients
                .filter((recipient) => recipient.checked && recipient.persona?.id)
                .map((recipient) => recipient.persona.id),
            default_res_ids: [thread.id],
            default_subtype_xmlid: "mail.mt_comment",
            mail_post_autofollow: thread.hasWriteAccess,
            body_contains_signature_only: !body || body.trim().length === 0,
        };
        await this.action.doAction(
            {
                name: _t("Compose Email"),
                type: "ir.actions.act_window",
                res_model: "mail.compose.message",
                view_mode: "form",
                views: [[false, "form"]],
                target: "new",
                context,
            },
            {
                onClose: () => this.onCloseFullComposerCallback(),
            }
        );
    },

    async toggleComposer(mode = false) {
        if (mode !== "message") {
            return super.toggleComposer(...arguments);
        }
        this.closeSearch();
        const openComposer = () => this._openMessageFullComposer();
        if (this.state.thread.id) {
            return openComposer();
        }
        this.onThreadCreated = openComposer;
        return this.props.saveRecord?.();
    },
});
