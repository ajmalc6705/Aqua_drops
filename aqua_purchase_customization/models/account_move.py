from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class AccountMove(models.Model):
  
    _inherit = "account.move"
    
    is_aqua_bill = fields.Boolean(string="Is aqua bill")

class AccountPayment(models.Model):
  
    _inherit = "account.payment"
    
    is_aqua_coupon_payment = fields.Boolean(string="Is aqua coupon bill")
