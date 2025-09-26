odoo.define("pos_discount_decimal.PosDiscountDecimalButton", function (require) {
    "use strict";

    const DiscountButton = require("pos_discount.DiscountButton");
    const Registries = require("point_of_sale.Registries");

    const PosDiscountDecimalButton = (DiscountButton) => class extends DiscountButton {
        async onClick() {
            const { confirmed, payload } = await this.showPopup('NumberPopup',{
                title: this.env._t('Discount Percentage'),
                startingValue: this.env.pos.config.discount_pc,
            });
            if (confirmed) {
                const val = parseFloat(payload.replace(",", "."));
                await this.apply_discount(val);
            }
        }
    }

    Registries.Component.extend(DiscountButton, PosDiscountDecimalButton);

    return PosDiscountDecimalButton;
});
