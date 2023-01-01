from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AquaCustomerCoupon(models.Model):
  
    _name = "aqua.customer.coupon"
    _description = "Customer Coupon"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
        
    @api.model
    def _get_warehouse(self):
        loged_user = self.env.user
        current_branch_id = False
        if loged_user and loged_user.current_branch_id:
            current_branch_id = loged_user.current_branch_id.id
        return current_branch_id

    def _get_warehouse_domain(self):
        loged_user = self.env.user
        current_branch_ids = []
        if loged_user and loged_user.branch_ids:
            current_branch_ids = loged_user.branch_ids.ids
        return [('id', 'in', current_branch_ids)]
    
    @api.model
    def _get_is_branch_readonly(self):
        loged_user = self.env.user
        is_branch_readonly = False
        if loged_user and loged_user.current_branch_id:
            is_branch_readonly = True
        return is_branch_readonly

    warehouse_id = fields.Many2one('stock.warehouse',string="Branch",domain=_get_warehouse_domain, default=_get_warehouse)
    is_branch_readonly = fields.Boolean(string="Branch Visibility",default=_get_is_branch_readonly)
    name = fields.Char(string="Name")
    customer_id = fields.Many2one('res.partner',string="Customer")
    coupon_count = fields.Integer(string="Coupon Count",tracking=True)
    coupon_line_ids = fields.One2many('aqua.customer.coupon.lines','coupon_id',string="Coupon Lines")
    coupon_number = fields.Integer(string="Coupon Number")
    coupon_amount = fields.Float(string="Coupon Amount")
    amount = fields.Float(string="Total amount",compute='compute_total_amount',store=True)
    received_amount = fields.Float(string="Received Amount")
    register_payment = fields.Boolean(string="Is payment registered",compute='compute_register_payment',store=True)
    payment_ids = fields.Many2many('account.payment','aqua_coupon_payment_rel','payment_id','coupon_id',string="Payments")
    
    @api.depends('received_amount','amount')
    def compute_register_payment(self):
        for rec in self:
            register_payment = False
            if rec.amount == rec.received_amount:
                register_payment = True
            rec.register_payment = register_payment
    
    @api.depends('coupon_count','coupon_amount')
    def compute_total_amount(self):
        for rec in self:
            rec.amount = rec.coupon_count * rec.coupon_amount
    
    

    @api.model
    def create(self, vals):
        res = super(AquaCustomerCoupon, self).create(vals)
        res.name = self.env['ir.sequence'].next_by_code('aqua.coupon')
        return res

    
    def confirm_coupon(self):
	    for rec in self:
	        no = rec.coupon_number
	        for line in range(rec.coupon_count):
	            no = no + 1
	            line = self.env['aqua.customer.coupon.lines'].create({'coupon_id': rec.id, 'sl_no': no})

    @api.constrains('coupon_amount')
    def check_coupon_amount(self):
        for rec in self:
            if rec.coupon_amount <0:
                raise ValidationError(_("Coupon amount must be positive"))
    
class AquaCustomerCouponLines(models.Model):
  
    _name = "aqua.customer.coupon.lines"
    _description = "Customer Coupon Lines"   
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _rec_name = "sl_no"
        
    sl_no = fields.Integer(string="SL/No.")
    status = fields.Selection([('open','Open'),('used','Used')],string="Status",default='open',tracking=True)
    used_on = fields.Datetime(string="Used On",tracking=True)
    used_by = fields.Many2one('res.users', string="Used By",tracking=True)
    coupon_id = fields.Many2one('aqua.customer.coupon',string="Customer Coupon")
    customer_id = fields.Many2one('res.partner',string="Customer",compute="compute_customer",store=True)
    
    @api.depends('coupon_id','coupon_id.customer_id')
    def compute_customer(self):
        for rec in self:
            rec.customer_id = rec.coupon_id and rec.coupon_id.customer_id and rec.coupon_id.customer_id.id or False
            
    
    def action_used(self):
    	for rec in self:
    		rec.status = 'used'
    		rec.used_on = fields.Datetime.now()
    		rec.used_by = self.env.user.id
    
