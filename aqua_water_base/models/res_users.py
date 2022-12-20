from odoo import api, fields, models, _


class ResUsers(models.Model):
  
    _inherit = "res.users"
    _description = "Users"
    
    current_branch_id = fields.Many2one('stock.warehouse',string="Current Branch")
    branch_ids = fields.Many2many('stock.warehouse','res_users_stock_warehouse_relation','user_id','warehouse_id',string="Branch")
    
    @api.onchange('branch_ids')
    def onchange_branch_ids(self):
        for rec in self:
            rec.current_branch_id = False
            
    