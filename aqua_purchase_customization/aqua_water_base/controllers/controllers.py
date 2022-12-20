# -*- coding: utf-8 -*-
# from odoo import http


# class AquaWaterBase(http.Controller):
#     @http.route('/aqua_water_base/aqua_water_base', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/aqua_water_base/aqua_water_base/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('aqua_water_base.listing', {
#             'root': '/aqua_water_base/aqua_water_base',
#             'objects': http.request.env['aqua_water_base.aqua_water_base'].search([]),
#         })

#     @http.route('/aqua_water_base/aqua_water_base/objects/<model("aqua_water_base.aqua_water_base"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('aqua_water_base.object', {
#             'object': obj
#         })
