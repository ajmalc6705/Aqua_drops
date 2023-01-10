from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class AccountMove(models.Model):
  
    _inherit = "account.move"
    
    is_aqua_sale_bill = fields.Boolean(string="Is aqua sale bill")
    aqua_sale_id = fields.Many2one('sale.order',string="Sale")
    customer_due_amount = fields.Float(string="Total Due Amount",compute='compute_sale_due_amt')
    sale_picking_count = fields.Integer(string="Shipment Count",compute='compute_sale_picking_count')

    def action_view_sale(self):
        for rec in self:
            if rec.aqua_sale_id:
                form_view_id = self.env.ref('aqua_sale_customization.aqua_water_sale_order_form_view').id or False
                tree_view_id = self.env.ref('aqua_sale_customization.aqua_water_sale_order_tree_view').id or False
                return {
                    'name': _('Sale'),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                    'res_model': 'sale.order',
                    'type': 'ir.actions.act_window',
                    'domain': [('id', '=',rec.aqua_sale_id.id)],
                    'target': 'current',
                    'context':{'create': False,'edit': False,'delete':False}
                }
    
    def compute_sale_picking_count(self):
        for rec in self:
            pickings = self.env['stock.picking'].search([('invoice_id','=',rec.id)])
            rec.sale_picking_count = pickings and len(pickings.ids) or 0
    
    def view_all_sale_shipment(self):
        for rec in self:
            pickings = self.env['stock.picking'].search([('invoice_id','=',rec.id)])
            if pickings:
                form_view_id = self.env.ref('aqua_sale_customization.aqua_water_delivery_form_view').id or False
                tree_view_id = self.env.ref('aqua_sale_customization.aqua_water_delivery_tree_view').id or False
                return {
                    'name': _('Delivery'),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                    'res_model': 'stock.picking',
                    'type': 'ir.actions.act_window',
                    'domain': [('id','in',pickings and pickings.ids or [])],
                    'target': 'current',
                    'context':{'create': False,'edit': False,'delete':False}
                }

    def compute_sale_due_amt(self):
        for rec in self:
            bills = self.env['account.move'].search([('move_type','=','out_invoice'),('is_aqua_sale_bill','=',True),('partner_id','=',rec.partner_id.id)])
            amount = 0
            for line in bills:
                amount += line.amount_residual
            rec.customer_due_amount = amount
