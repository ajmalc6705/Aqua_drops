from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class StockPicking(models.Model):
  
    _inherit = "stock.picking"
    
    is_aqua_picking = fields.Boolean(string="Is aqua picking")
    invoice_id = fields.Many2one('account.move')
    
    def receive_shipment_action(self):
        shipment_wiz = self.env['shipment.receive.wiz']
        for record in self:
            context = self._context.copy()
            context.update({
                'active_model':'stock.picking',
                'active_id':record.id,
                'active_ids':[record.id],
            })
            shipment_obj = shipment_wiz.with_context(context).create({})
            form_view_id = self.env.ref('aqua_purchase_customization.aqua_shipment_wiz_form').id
            return {
                'name': _('Receive Shipment'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'shipment.receive.wiz',
                'views': [(form_view_id, 'form')],
                'view_id': form_view_id,
                'target': 'new',
                'res_id': shipment_obj.id,
            }

    def button_validate(self):
        res = super(StockPicking,self).button_validate()
        for rec in self:
            if rec.move_lines:
                for line in rec.move_lines.move_line_ids:
                    if line.lot_id:
                        line.lot_id.expiry_date = line.move_id.expiry_date
            if rec.state=='done':
                rec.aqua_action_create_invoice()
        return res
    


    def _aqua_prepare_invoice(self, po,journal):
        self.ensure_one()
        move_type = self._context.get('default_move_type', 'in_invoice')
        journal = self.env['account.move'].with_context(default_move_type=move_type)._get_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting purchase journal for the company %s (%s).') % (self.company_id.name, self.company_id.id))
        picking_id = self.id
        invoice_vals = {
            'ref': '',
            'move_type': move_type,
            'currency_id': po.currency_id.id,
            'invoice_user_id': self.env.user.id,
            'partner_id': po.partner_id.id,
            'fiscal_position_id': (po.fiscal_position_id or po.fiscal_position_id.get_fiscal_position(po.partner_id.id)).id,
            'invoice_origin': po.name or '' + '/',
            'invoice_line_ids': [],
            'company_id': po.company_id.id,
            'picking_id': picking_id,
            'invoice_date': po.date_order,
            'purchase_id': po and po.id,
            'journal_id': journal and journal.id,
            'is_aqua_bill':True,
            'warehouse_id':po.warehouse_id and po.warehouse_id.id or False
        }
        return invoice_vals

    def aqua_action_create_invoice(self):
        po = self.purchase_id
        sequence = 0
        move_type = self._context.get('default_move_type', 'in_invoice')
        journal = self.env['account.move'].with_context(default_move_type=move_type)._get_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting purchase journal for the company %s (%s).') % (self.company_id.name, self.company_id.id))
        
        # journal = self.env['account.journal'].search([('type', '=', 'purchase')], limit=1)
        invoice_vals = self._aqua_prepare_invoice(po,journal)
        picking_id = self
        for line in self.move_ids_without_package:
            line_vals = self._prepare_aqua_account_move_line(line, picking_id,journal)
            line_vals.update({'sequence': sequence})
            invoice_vals['invoice_line_ids'].append((0, 0, line_vals))
            sequence += 1
            

        if invoice_vals:
            AccountMove = self.env['account.move'].with_context(default_move_type='in_invoice')
            invoice_id = AccountMove.create(invoice_vals)
            invoice_id.action_post()
            picking_id.write({'invoice_id': invoice_id.id})

    def _prepare_aqua_account_move_line(self, line=False, picking_id=False,journal=False):
        account_id = journal.default_account_id
        if not account_id:
            raise ValidationError("Expense Account not configured")
        aml_currency = self.purchase_id and self.purchase_id.currency_id
        date = fields.Date.today()
        res = {}
        if line.quantity_done>0:
            res = {
                'name': '%s: %s' % (self.purchase_id.name, picking_id.name),
                'product_id': line.product_id.id,
                'product_uom_id': line.purchase_line_id.product_uom.id,
                'quantity': line.quantity_done,
                'tax_ids': [(6, 0, line.purchase_line_id.taxes_id.ids)],
                'price_unit': self.purchase_id.currency_id._convert(line.purchase_line_id.price_unit, aml_currency, self.purchase_id.company_id, date, round=False),
                'purchase_line_id': line.purchase_line_id.id,
                'account_id': account_id.id
            }
        if not line:
            return res
    
        return res


class StockMove(models.Model):
  
    _inherit = "stock.move"
    
    expiry_date = fields.Date(string="Expiry Date")
    pending_qty = fields.Float(compute='compute_pending_qty',store=True, string='Pending Qty')
    
    @api.depends('product_uom_qty', 'quantity_done')
    def compute_pending_qty(self):
        for rec in self:
            pending_qty = rec.product_uom_qty
            if rec.quantity_done:
                pending_qty -= rec.quantity_done

            rec.pending_qty = pending_qty

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

class StockMoveLine(models.Model):
  
    _inherit = "stock.move.line"
    
    purchase_line_id = fields.Many2one('purchase.order.line')

