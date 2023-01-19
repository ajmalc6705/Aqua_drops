from odoo import api, fields, models, _


class Warehouse(models.Model):
  
    _inherit = "stock.warehouse"
    _description = "Branch"

    is_aqua_branch = fields.Boolean(string="Is Aqua Branch", default=True)
    phone = fields.Char()
    email = fields.Char()
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char()
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    users_ids = fields.Many2many('res.users','res_users_stock_warehouse_relation','warehouse_id','user_id',string="Allowed Users")
    sequence_id = fields.Many2one('ir.sequence',string="Sequence")
    last_used_nbr = fields.Integer(string="Last used coupon no")
    customer_coupon_ids = fields.One2many('aqua.customer.coupon', 'warehouse_id')
    
    # aqua_stock_warehouse_res_user_rel
    def create_partner(self):
        for rec in self:
            partner = self.env['res.partner'].create({'name': rec.name,
                                                      'street':rec.street,
                                                      'street2':rec.street2,
                                                      'zip':rec.zip,
                                                      'city':rec.city,
                                                      'state_id':rec.state_id and rec.state_id.id or False,
                                                      'country_id':rec.country_id and rec.country_id.id or False,
                                                      'email':rec.email,
                                                      'phone':rec.phone,
                                                      'is_branch_customer':True
                                                    })
            rec.partner_id = partner.id
    
    def create_sequence(self):
        for rec in self:
            sequence = self.env['ir.sequence'].create({
                    'name': '%s Branch Sequence' % str(rec.name),
                    'code': 'Branch%s-%s' % (rec.name, rec.code),
                    'implementation': 'no_gap',
                    'company_id': self.env.user and self.env.user.company_id.id or False,
                    'prefix': 'CC/%s/'%(str(rec.code)),
                    'padding': 5,
                    'number_next': 1,
                    'number_increment': 1
                })
            rec.sequence_id = sequence and sequence.id or False



    @api.model
    def create(self, vals):
        res = super(Warehouse, self.sudo()).create(vals)
        res.create_partner()
        res.create_sequence()
        return res
