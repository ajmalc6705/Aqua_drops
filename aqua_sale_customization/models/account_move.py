from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class AccountMove(models.Model):
  
    _inherit = "account.move"
    
    is_aqua_sale_bill = fields.Boolean(string="Is aqua sale bill")
    aqua_sale_id = fields.Many2one('sale.order',string="Sale")
