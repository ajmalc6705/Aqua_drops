# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Imazighen Web Enterprise',
    "category": "Theme/Backend",
    "version": "15.0.1.0.0",
    'author': 'Imazighen',
    'currency': 'EUR',
    'price': 45.0,
    'depends': ['web'],
    
    'description': """This module provide Enterprise design and responsiveness.
        """,

    'depends': ['web'],
    'images': ['static/description/home.gif'],
    'auto_install': False,
    'data': [
        'views/partner_view.xml',
        'views/webclient_templates.xml',
    ],
    'assets': {
        'web.assets_qweb': [
            'imazighen_web_enterprise/static/src/**/*.xml',
        ],
        'web._assets_primary_variables': [
            ('prepend', 'imazighen_web_enterprise/static/src/legacy/scss/primary_variables.scss'),
        ],
        'web._assets_secondary_variables': [
            'imazighen_web_enterprise/static/src/legacy/scss/secondary_variables.scss',
        ],
        'web._assets_backend_helpers': [
            'imazighen_web_enterprise/static/src/legacy/scss/bootstrap_overridden.scss',
        ],
        'web._assets_common_styles': [
            ('replace', 'web/static/src/legacy/scss/ui_extra.scss', 'imazighen_web_enterprise/static/src/legacy/scss/ui.scss'),

            'imazighen_web_enterprise/static/fonts/fonts.scss',
        ],
        'web.assets_backend': [
            ('replace', 'web/static/src/webclient/webclient_extra.scss', 'imazighen_web_enterprise/static/src/webclient/webclient.scss'),
            ('replace', 'web/static/src/webclient/webclient_layout.scss', 'imazighen_web_enterprise/static/src/webclient/webclient_layout.scss'),

            ('replace', 'web/static/src/legacy/scss/dropdown_extra.scss', 'imazighen_web_enterprise/static/src/legacy/scss/fields.scss'),
            ('replace', 'web/static/src/legacy/scss/fields_extra.scss', 'imazighen_web_enterprise/static/src/legacy/scss/form_view.scss'),
            ('replace', 'web/static/src/legacy/scss/form_view_extra.scss', 'imazighen_web_enterprise/static/src/legacy/scss/list_view.scss'),
            ('replace', 'web/static/src/legacy/scss/list_view_extra.scss', 'imazighen_web_enterprise/static/src/legacy/scss/search_view.scss'),
            ('replace', 'web/static/src/search/search_panel/search_view_extra.scss', 'imazighen_web_enterprise/static/src/legacy/scss/dropdown.scss'),
            ('replace', 'mail/static/src/widgets/form_renderer/form_renderer.scss', 'imazighen_web_enterprise/static/src/form_renderer/scss/form_renderer.scss'),

            'imazighen_web_enterprise/static/src/legacy/scss/base_settings_mobile.scss',
            'imazighen_web_enterprise/static/src/legacy/scss/search_panel_mobile.scss',
            'imazighen_web_enterprise/static/src/legacy/scss/menu_search.scss',
            'imazighen_web_enterprise/static/src/legacy/scss/control_panel_layout.scss',
            'imazighen_web_enterprise/static/src/legacy/scss/control_panel_mobile.scss',
            'imazighen_web_enterprise/static/src/legacy/scss/kanban_view.scss',
            'imazighen_web_enterprise/static/src/legacy/scss/touch_device.scss',
            'imazighen_web_enterprise/static/src/legacy/scss/snackbar.scss',
            'imazighen_web_enterprise/static/src/legacy/scss/swipe_item_mixin.scss',
            'imazighen_web_enterprise/static/src/legacy/scss/form_view_mobile.scss',
            'imazighen_web_enterprise/static/src/legacy/scss/kanban_view_mobile.scss',
            'imazighen_web_enterprise/static/src/legacy/scss/modal_mobile.scss',
            'imazighen_web_enterprise/static/src/legacy/scss/promote_studio.scss',
            'imazighen_web_enterprise/static/src/legacy/scss/web_calendar_mobile.scss',
            'imazighen_web_enterprise/static/src/legacy/scss/barcodes_mobile.scss',
            'imazighen_web_enterprise/static/src/legacy/scss/pivot_view_mobile.scss',
            'imazighen_web_enterprise/static/src/search/**/*.scss',
            'imazighen_web_enterprise/static/src/webclient/**/*.scss',
            'imazighen_web_enterprise/static/src/views/**/*.scss',

             ('replace', 'web/static/src/legacy/js/fields/upgrade_fields.js', 'imazighen_web_enterprise/static/src/legacy/js/apps.js'),

             'imazighen_web_enterprise/static/src/search/**/*.js',
             'imazighen_web_enterprise/static/src/webclient/**/*.js',
             'imazighen_web_enterprise/static/src/views/**/*.js',

             'imazighen_web_enterprise/static/src/legacy/**/*.js',
             ("remove", "imazighen_web_enterprise/static/src/legacy/js/views/pivot_renderer.js"),
        ],
        "web.assets_backend_legacy_lazy": [
            "imazighen_web_enterprise/static/src/legacy/js/views/pivot_renderer.js",
        ],
        'web.assets_backend_prod_only': [
            ('replace', 'web/static/src/main.js', 'imazighen_web_enterprise/static/src/main.js'),
        ],
        'web.tests_assets': [
            'imazighen_web_enterprise/static/tests/*.js',
        ],
        'web.qunit_suite_tests': [
            ('remove', 'web/static/tests/legacy/fields/upgrade_fields_tests.js'),

            'imazighen_web_enterprise/static/tests/webclient/**/*.js',

            'imazighen_web_enterprise/static/tests/legacy/upgrade_fields_tests.js',
            'imazighen_web_enterprise/static/tests/legacy/views/list_tests.js',
            'imazighen_web_enterprise/static/tests/legacy/barcodes_tests.js',
        ],
        'web.qunit_mobile_suite_tests': [
            'imazighen_web_enterprise/static/tests/mobile/**/*.js',

            'imazighen_web_enterprise/static/tests/legacy/action_manager_mobile_tests.js',
            'imazighen_web_enterprise/static/tests/legacy/control_panel_mobile_tests.js',
            'imazighen_web_enterprise/static/tests/legacy/form_mobile_tests.js',
            'imazighen_web_enterprise/static/tests/legacy/relational_fields_mobile_tests.js',
            'imazighen_web_enterprise/static/tests/legacy/views/basic/basic_render_mobile_tests.js',
            'imazighen_web_enterprise/static/tests/legacy/views/calendar_mobile_tests.js',
            'imazighen_web_enterprise/static/tests/legacy/views/kanban_mobile_tests.js',
            'imazighen_web_enterprise/static/tests/legacy/views/list_mobile_tests.js',
            'imazighen_web_enterprise/static/tests/legacy/base_settings_mobile_tests.js',
            'imazighen_web_enterprise/static/tests/legacy/components/action_menus_mobile_tests.js',
            'imazighen_web_enterprise/static/tests/legacy/barcodes_mobile_tests.js',
        ],
    },
    'license': 'OEEL-1',
}
