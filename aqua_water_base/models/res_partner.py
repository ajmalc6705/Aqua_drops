from odoo import api, fields, models, _


class ResPartner(models.Model):
  
    _inherit = "res.partner"
    
    def _get_warehouse_domain(self):
        loged_user = self.env.user
        current_branch_ids = []
        if loged_user and loged_user.branch_ids:
            current_branch_ids = loged_user.branch_ids.ids
        return [('id', 'in', current_branch_ids)]
    
    warehouse_id = fields.Many2one('stock.warehouse',string="Branch",domain=_get_warehouse_domain)
    is_aqua_customer = fields.Boolean(string="Is aqua customer")
    is_branch_customer = fields.Boolean(string="Is branch customer")
    is_aqua_vendor = fields.Boolean(string="Is aqua vendor")
    account_move_ids = fields.One2many('account.move','partner_id',string="Bills")
    coupon_count = fields.Boolean(string="Coupons",compute="compute_coupon_count")
    
    def compute_coupon_count(self):
        for rec in self:
            coupons = self.env['aqua.customer.coupon'].search([('customer_id','=',rec.id)])
            rec.coupon_count = coupons and len(coupons.ids) or 0
    
    def view_all_coupons(self):
        for rec in self:
            coupons = self.env['aqua.customer.coupon'].search([('customer_id','=',rec.id)])
            if coupons:
                form_view_id = self.env.ref('aqua_water_base.aqua_water_customer_coupon_form_view').id or False
                tree_view_id = self.env.ref('aqua_water_base.aqua_water_customer_coupon_tree_view').id or False
                return {
                    'name': _('Coupons'),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                    'res_model': 'aqua.customer.coupon',
                    'type': 'ir.actions.act_window',
                    'domain': [('id', 'in', coupons.ids or [])],
                    'target': 'current',
                    'context':{'create': False,'edit': False,'delete':False}
                }
    
