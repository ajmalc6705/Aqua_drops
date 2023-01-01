# -*- coding: utf-8 -*-
{
    'name': "aqua_water_base",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','account'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'wizard/payment_wizard_view.xml',
        'views/stock_warehouse.xml',
        'views/customer_coupon.xml',
        'views/res_users.xml',
        'views/res_partner.xml',
        'views/product.xml',
        'views/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
