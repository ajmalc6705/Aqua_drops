from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class AccountMove(models.Model):
  
    _inherit = "account.move"
    
    is_aqua_bill = fields.Boolean(string="Is aqua bill")
    warehouse_id = fields.Many2one('stock.warehouse',string="Branch")
    picking_id = fields.Many2one('stock.picking')
