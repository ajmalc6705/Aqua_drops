from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class StockProductionLot(models.Model):
  
    _inherit = "stock.production.lot"
    
    expiry_date = fields.Date(string="Expiry Date")
    is_aqua_lot = fields.Boolean(string="Is aqua lot")
    purchase_line_id = fields.Many2one('purchase.order.line')
    batch_number = fields.Char(string='Batch Number',size=10)
    location_id = fields.Many2one('stock.location',string="location",ondelete='restrict')
    warehouse_id = fields.Many2one('stock.warehouse',string="Branch")
    partner_id = fields.Many2one('res.partner',string="Vendor",ondelete='restrict')
    unit_price = fields.Float(string="Unit Price")
    taxes_ids = fields.Many2many('account.tax', 'stock_production_lot_account_tax_relation','stock_id','tax_id',string='Taxes')
    subtotal = fields.Float(string="Total Price",compute='_compute_amount',store=True)
    tax_amount = fields.Float(string="Tax Amount",compute='_compute_amount',store=True)
    price_total = fields.Float(string="Total Amount",compute='_compute_amount',store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)

    @api.depends('product_qty', 'unit_price', 'taxes_ids')
    def _compute_amount(self):
        for line in self:
            vals = line._prepare_compute_all_values()
            taxes = line.taxes_ids.compute_all(
                vals['unit_price'],
                vals['currency_id'],
                vals['product_qty'],
                vals['product'],
                vals['partner'])
            line.update({
                'tax_amount': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'subtotal': taxes['total_excluded'],
            })

    def _prepare_compute_all_values(self):
        self.ensure_one()
        return {
            'unit_price': self.unit_price,
            'currency_id': self.currency_id,
            'product_qty': self.product_qty,
            'product': self.product_id,
            'partner': self.partner_id,
        }

    @api.constrains('name')
    def check_duplicate_name(self):
        for rec in self:
            similar_item = self.search([('name','=',rec.name),('id','!=',rec.id)], limit=1)
            if similar_item:
                raise ValidationError(_("There is already a Barcode generated against %s with Batch Number as %s.!"
                                      %(similar_item[0].product_id.name,similar_item[0].batch_number and similar_item[0].batch_number.upper())))
                               
    def check_duplicate_batch_number(self, product_id, batch_number):
        for lot in self.search([('product_id','=', product_id), ('batch_number','!=', False)]):
            skip = False
            if (not skip) and lot.batch_number and lot.batch_number.upper() == str(batch_number).upper():
                raise ValidationError(_("There is already a Barcode generated against %s with Batch Number as %s.!"
                                      %(lot.product_id.name,batch_number.upper())))


