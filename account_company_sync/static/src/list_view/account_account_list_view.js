/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { ListController } from "@web/views/list/list_controller";
import { listView } from "@web/views/list/list_view";
import { useService } from "@web/core/utils/hooks";

class AccountListController extends ListController {
    setup() {
        super.setup()
        this.actionService = useService("action");
        this.notification = useService("notification");
    }
    async SyncAccounts() {
        await this.actionService.doAction("account_company_sync.action_queue_sync_all_accounts");
        this.notification.add(_t("Chart of Acconts correctly queue"), { type: "success" });
    }
}

export const accountListView = {
    ...listView,
    Controller: AccountListController,
    buttonTemplate: "account_company_sync.AccountListView.Buttons",
}

registry.category("views").add("account_account_list_view", accountListView);
