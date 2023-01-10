from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class AccountMove(models.Model):
  
    _inherit = "account.move"
    
    is_aqua_bill = fields.Boolean(string="Is aqua bill")
    vendor_due_amount = fields.Float(string="Total Due Amount",compute='compute_po_due_amt')
    picking_count = fields.Integer(string="Shipment Count",compute='compute_picking_count')
    po_attachment = fields.Binary(string='Attachment', attachment=True)
    po_file_name = fields.Char(string="File name")
    source_document = fields.Char()

    def compute_picking_count(self):
        for rec in self:
            pickings = self.env['stock.picking'].search([('invoice_id','=',rec.id)])
            rec.picking_count = pickings and len(pickings.ids) or 0
    
    def view_all_shipment(self):
        for rec in self:
            pickings = self.env['stock.picking'].search([('invoice_id','=',rec.id)])
            if pickings:
                form_view_id = self.env.ref('aqua_purchase_customization.aqua_water_shipment_form_view').id or False
                tree_view_id = self.env.ref('aqua_purchase_customization.aqua_water_shipment_tree_view').id or False
                return {
                    'name': _('Shipment'),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                    'res_model': 'stock.picking',
                    'type': 'ir.actions.act_window',
                    'domain': [('id','in',pickings and pickings.ids or [])],
                    'target': 'current',
                    'context':{'create': False,'edit': False,'delete':False}
                }

    def compute_po_due_amt(self):
        for rec in self:
            bills = self.env['account.move'].search([('move_type','=','in_invoice'),('is_aqua_bill','=',True),('partner_id','=',rec.partner_id.id)])
            amount = 0
            for line in bills:
                amount += line.amount_residual
            rec.vendor_due_amount = amount

    def action_view_po(self):
        for rec in self:
            if rec.purchase_id:
                form_view_id = self.env.ref('aqua_purchase_customization.aqua_water_purchase_form_view').id or False
                tree_view_id = self.env.ref('aqua_purchase_customization.aqua_water_purchase_tree_view').id or False
                return {
                    'name': _('Purchase Order'),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                    'res_model': 'purchase.order',
                    'type': 'ir.actions.act_window',
                    'domain': [('id', '=',rec.purchase_id.id)],
                    'target': 'current',
                    'context':{'create': False,'edit': False,'delete':False}
                }

class AccountPayment(models.Model):
  
    _inherit = "account.payment"
    
    is_aqua_coupon_payment = fields.Boolean(string="Is aqua coupon bill")
