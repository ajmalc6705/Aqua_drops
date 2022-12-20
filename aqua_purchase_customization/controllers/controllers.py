# -*- coding: utf-8 -*-
# from odoo import http


# class AquaPurchaseCustomization(http.Controller):
#     @http.route('/aqua_purchase_customization/aqua_purchase_customization', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/aqua_purchase_customization/aqua_purchase_customization/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('aqua_purchase_customization.listing', {
#             'root': '/aqua_purchase_customization/aqua_purchase_customization',
#             'objects': http.request.env['aqua_purchase_customization.aqua_purchase_customization'].search([]),
#         })

#     @http.route('/aqua_purchase_customization/aqua_purchase_customization/objects/<model("aqua_purchase_customization.aqua_purchase_customization"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('aqua_purchase_customization.object', {
#             'object': obj
#         })
