from odoo import api, fields, models, _


class Warehouse(models.Model):
  
    _inherit = "stock.warehouse"
    _description = "Branch"

    is_aqua_branch = fields.Boolean(string="Is Aqua Branch")
    phone = fields.Char()
    email = fields.Char()
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char()
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    users_ids = fields.Many2many('res.users','res_users_stock_warehouse_relation','warehouse_id','user_id',string="Allowed Users")

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

    @api.model
    def create(self, vals):
        res = super(Warehouse, self.sudo()).create(vals)
        res.create_partner()
        return res
