from odoo import api, fields, models, _


class ResUsers(models.Model):
  
    _inherit = "res.users"
    _description = "Users"
    
    branch_ids = fields.Many2many('stock.warehouse','res_users_stock_warehouse_relation','user_id','warehouse_id',string="Branch")
    
            
    