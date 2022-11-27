/** @odoo-module **/

import { UserMenu } from "@web/webclient/user_menu/user_menu";

export class BurgerUserMenu extends UserMenu {
    _onItemClicked(callback) {
        callback();
    }
}
BurgerUserMenu.template = "imazighen_web_enterprise.BurgerUserMenu";
