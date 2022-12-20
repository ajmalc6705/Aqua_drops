from odoo import api, fields, models, _


class Product(models.Model):
  
    _inherit = "product.product"
    
    @api.model
    def default_get(self, fields):
        result = super(Product,self).default_get(fields)
        result['type'] = 'product'
        return result
    
    is_aqua_product = fields.Boolean(string="Is aqua product")
    
