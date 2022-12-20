from odoo import api, fields, models, _


class AquaCustomerCoupon(models.Model):
  
    _name = "aqua.customer.coupon"
    _description = "Customer Coupon"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
        
    name = fields.Char(string="Name")
    customer_id = fields.Many2one('res.partner',string="Customer")
    coupon_count = fields.Integer(string="Coupon Count",tracking=True)
    coupon_line_ids = fields.One2many('aqua.customer.coupon.lines','coupon_id',string="Coupon Lines")
    warehouse_id = fields.Many2one('stock.warehouse',string="Branch")
    
    def confirm_coupon(self):
	    for rec in self:
	        no = 0
	        for line in range(rec.coupon_count):
	            no = no + 1
	            line = self.env['aqua.customer.coupon.lines'].create({'coupon_id': rec.id, 'sl_no': no})
    
class AquaCustomerCouponLines(models.Model):
  
    _name = "aqua.customer.coupon.lines"
    _description = "Customer Coupon Lines"   
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
        
    sl_no = fields.Integer(string="SL/No.")
    status = fields.Selection([('open','Open'),('used','Used')],string="Status",default='open',tracking=True)
    used_on = fields.Datetime(string="Used On",tracking=True)
    used_by = fields.Many2one('res.users', string="Used By",tracking=True)
    coupon_id = fields.Many2one('aqua.customer.coupon',string="Customer Coupon")
    
    def action_used(self):
    	for rec in self:
    		rec.status = 'used'
    		rec.used_on = fields.Datetime.now()
    		rec.used_by = self.env.user.id
    
