from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class AccountMove(models.Model):
  
    _inherit = "account.move"
    
    warehouse_id = fields.Many2one('stock.warehouse',string="Branch")
    picking_id = fields.Many2one('stock.picking')
    purchase_id = fields.Many2one('purchase.order', store=True,string='Purchase Order')
    picking_id = fields.Many2one('stock.picking', string="Picking")


class AccountMoveLine(models.Model):
  
    _inherit = "account.move.line"
    
    picking_line_id = fields.Many2one('stock.move',string="Move")

class StockPicking(models.Model):
  
    _inherit = "stock.picking"
    _order = 'id desc'
    
    invoice_id = fields.Many2one('account.move')

