# -*- coding: utf-8 -*-
{
    'name': "aqua_purchase_customization",

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
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['aqua_water_base','purchase_stock'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/receive_shipment_wiz.xml',
        'views/purchase_view.xml',
        'views/stock_picking.xml',
        'views/stock_move.xml',
        'views/account_move.xml',
        'views/menu.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
