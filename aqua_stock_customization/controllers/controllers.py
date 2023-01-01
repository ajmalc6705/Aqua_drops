# -*- coding: utf-8 -*-
# from odoo import http


# class AquaStockCustomization(http.Controller):
#     @http.route('/aqua_stock_customization/aqua_stock_customization', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/aqua_stock_customization/aqua_stock_customization/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('aqua_stock_customization.listing', {
#             'root': '/aqua_stock_customization/aqua_stock_customization',
#             'objects': http.request.env['aqua_stock_customization.aqua_stock_customization'].search([]),
#         })

#     @http.route('/aqua_stock_customization/aqua_stock_customization/objects/<model("aqua_stock_customization.aqua_stock_customization"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('aqua_stock_customization.object', {
#             'object': obj
#         })
