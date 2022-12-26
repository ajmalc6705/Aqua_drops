from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class StockPicking(models.Model):
  
    _inherit = "stock.picking"
    
    is_aqua_sale_picking = fields.Boolean(string="Is aqua sale picking")
