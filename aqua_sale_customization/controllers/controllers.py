# -*- coding: utf-8 -*-
# from odoo import http


# class AquaSaleCustomization(http.Controller):
#     @http.route('/aqua_sale_customization/aqua_sale_customization', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/aqua_sale_customization/aqua_sale_customization/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('aqua_sale_customization.listing', {
#             'root': '/aqua_sale_customization/aqua_sale_customization',
#             'objects': http.request.env['aqua_sale_customization.aqua_sale_customization'].search([]),
#         })

#     @http.route('/aqua_sale_customization/aqua_sale_customization/objects/<model("aqua_sale_customization.aqua_sale_customization"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('aqua_sale_customization.object', {
#             'object': obj
#         })
