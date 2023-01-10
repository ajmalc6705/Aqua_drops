from odoo import models, fields,api,_
from odoo.exceptions import ValidationError,UserError


class StockPickingValidate(models.TransientModel):
    _name = 'stock.picking.validate'
    _description = 'Validate receive shipment'

    @api.model
    def default_get(self, fields_list):
        res = super(StockPickingValidate, self).default_get(fields_list)
        if self._context.get('active_model') == 'stock.picking' and self._context.get('active_id'):
            picking_id = self.env['stock.picking'].browse(self._context.get('active_id'))
            res.update({'picking_id': self._context.get('active_id'),
                        'purchase_id': picking_id.purchase_id and picking_id.purchase_id.id or False,
                        'partner_id': picking_id.partner_id and picking_id.partner_id.id or False})
        return res

    @api.model
    def get_lines(self):
        lines = []
        if self._context.get('active_model') == 'stock.picking' and self._context.get('active_id'):
            picking_id = self.env['stock.picking'].browse(self._context.get('active_id'))
            wiz_line_pool = self.env['stock.picking.validate.lines']
            if picking_id:
                for line in picking_id.move_lines:
                    line = wiz_line_pool.create({
                        'product_id': line.product_id and line.product_id.id or False,
                        'product_uom': line.product_uom and line.product_uom.id or line.product_id and line.product_id.uom_po_id \
                                       and line.product_id.uom_po_id.id or False,
                        'quantity': line.product_uom_qty or 0,
                        'receiving_qty': line.product_uom_qty or 0,
                        'move_id': line.id,
                        'expiry_date':line.expiry_date,
                        'purchase_line_id': line.purchase_line_id and line.purchase_line_id.id or False,
                        'warehouse_id': line.purchase_line_id and line.purchase_line_id.order_id and \
                                        line.purchase_line_id.order_id.warehouse_id and line.purchase_line_id.order_id.warehouse_id.id or False,
                    })
                    lines.append(line.id)
        return lines

    vendor_bill = fields.Char('Vendor Bill No')
    bill_date = fields.Date(string='Bill Date', default=fields.Date.today)
    picking_id = fields.Many2one('stock.picking', string="Shipment Ref.")
    partner_id = fields.Many2one('res.partner', string="Supplier")
    purchase_id = fields.Many2one('purchase.order', string="Purchase Order")
    wiz_line_ids = fields.One2many('stock.picking.validate.lines', 'wiz_id', default=get_lines)
    stock_receive_date = fields.Date(string="Received Date", default=fields.Date.today)
    po_attachment = fields.Binary(string='Attachment', attachment=True)
    po_file_name = fields.Char(string="File name")

    @api.constrains('bill_date')
    def check_bill_date(self):
        for rec in self:
            today = fields.Date.context_today(self)
            if rec.bill_date:
                if rec.bill_date > today:
                    raise ValidationError(_('Bill date cannot be future data'))


    def _get_internal_picking(self):
        company = self.env['res.company']._company_default_get('stock.picking')
        internal_picking = self.env['stock.picking.type'].search(
            [('warehouse_id.company_id', '=', company.id), ('code', '=', 'internal')],
            limit=1,
        )
        return internal_picking

    def action_validate(self):
        lot_pool = self.env['stock.production.lot']
        for rec in self:
            if rec.picking_id:
                if rec.po_attachment:
                    rec.picking_id.write({'po_attachment': rec.po_attachment,
                                         'po_file_name': rec.po_file_name,
                                          'document_number': rec.vendor_bill
                                        })

                    attachment = self.env['po.attachment.lines'].create({'po_attachment': rec.po_attachment,
                                                                         'po_file_name': rec.po_file_name,
                                                                         'purchase_id': rec.purchase_id and rec.purchase_id.id or False,
                                                                         'document_number': rec.vendor_bill,
                                                                         'document_date': rec.bill_date})
                warehouse_data = {}
                for line in rec.wiz_line_ids.filtered(lambda i: i.receiving_qty > 0):
                    if not line.expiry_date:
                        raise ValidationError(_("Please provide Expiry Date for %s.!"%line.product_id.name))
                    if not line.warehouse_id in warehouse_data:
                        warehouse_data.update(
                            {line.warehouse_id: [line.id]})
                    else:
                        warehouse_data[line.warehouse_id].append(line.id)
                    batch_no = line.batch_number and line.batch_number.upper() or ''
                    for picking_move in rec.picking_id.move_lines.filtered(lambda m: m.product_id == line.product_id and \
                                                                           m.purchase_line_id == line.purchase_line_id):
                        old_move_line = picking_move.move_line_ids[0]

                    move_line = old_move_line.copy()
                    move_line.product_uom_qty = line.receiving_qty
                    lot_name = line.get_lot_name(move_line)
                    lot_id = lot_pool.create({
                        'name': lot_name,
                        'product_id': move_line.product_id.id,
                        'partner_id': rec.purchase_id and rec.purchase_id.partner_id and rec.purchase_id.partner_id.id or False,
                        'unit_price': line.purchase_line_id.price_unit or 0.00,
                        'purchase_line_id': line.purchase_line_id.id,
                        'qty': line.purchase_line_id.product_qty,
                        'batch_number': line.batch_number,
                        'expiry_date': line.expiry_date,
                        'taxes_ids': [(6, 0, line.purchase_line_id.taxes_id and line.purchase_line_id.taxes_id.ids or [])],
                        'company_id': line.purchase_line_id.order_id.company_id.id,
                        'is_aqua_lot':True
                    })
                    line.lot_id = lot_id.id
                    move_line.lot_id = lot_id.id
                    move_line.qty_done = move_line.product_uom_qty
                    old_move_line.unlink()
                rec.picking_id.stock_receive_date = rec.stock_receive_date
                if rec.picking_id._check_backorder():
                    back_order = self.env['stock.backorder.confirmation'].with_context({'button_validate_picking_ids': [rec.picking_id.id]}).create(
                        {'pick_ids': [(4, rec.picking_id.id)]})
                    back_order.process()
                else:
                    rec.picking_id._action_done()

                for move in rec.picking_id.move_lines:
                    move.date = move.date.replace(month=rec.stock_receive_date.month, day=rec.stock_receive_date.day,
                                                  year=rec.stock_receive_date.year)
                    for line in move.move_line_ids:
                        line.date = line.date.replace(month=rec.stock_receive_date.month, day=rec.stock_receive_date.day,
                                                      year=rec.stock_receive_date.year)
                rec.aqua_action_create_picking_invoice()
            else:
                raise ValidationError(_("Shipment is not connected.!"))


    def _prepare_invoice(self):
        """Prepare the dict of values to create the new invoice for a purchase order.
        """
        self.ensure_one()
        move_type = self._context.get('default_move_type', 'in_invoice')
        journal = self.env['account.move'].with_context(default_move_type=move_type)._get_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting purchase journal for the company %s (%s).') % (self.company_id.name, self.company_id.id))

        partner_invoice_id = self.partner_id.address_get(['invoice'])['invoice']
        invoice_vals = {
            'ref': self.vendor_bill or '',
            'source_document': self.purchase_id.name,
            'move_type': move_type,
            'currency_id': self.purchase_id.currency_id.id,
            'invoice_user_id': self.env.user.id,
            'partner_id': partner_invoice_id,
            'fiscal_position_id': (self.purchase_id.fiscal_position_id or self.purchase_id.fiscal_position_id.get_fiscal_position(partner_invoice_id)).id,
            'invoice_origin': self.purchase_id.name or '' + '/' + self.vendor_bill,
            'invoice_line_ids': [],
            'company_id': self.purchase_id.company_id.id,
            'is_aqua_bill': True,
            'picking_id': self.picking_id.id,
            'invoice_date': self.bill_date,
            'purchase_id':self.purchase_id and self.purchase_id.id or False,
            'po_attachment':self.po_attachment,
            'po_file_name':self.po_file_name
        }
        return invoice_vals

    def aqua_action_create_picking_invoice(self):
        for rec in self:
            sequence = 0
            invoice_vals = self._prepare_invoice()
            for line in rec.wiz_line_ids.filtered(lambda i: i.receiving_qty > 0):
                line_vals = self._prepare_account_move_line(line)
                line_vals.update({'sequence': sequence})
                invoice_vals['invoice_line_ids'].append((0, 0, line_vals))
                sequence += 1

            if invoice_vals:
                AccountMove = self.env['account.move'].with_context(default_move_type='in_invoice')
                invoice_id = AccountMove.create(invoice_vals)
                invoice_id.post()
                rec.picking_id.invoice_id = invoice_id.id

    def _prepare_account_move_line(self, line=False):
        self.ensure_one()
        aml_currency = self.purchase_id and self.purchase_id.currency_id
        date = self.bill_date or fields.Date.today()
        res = {
            'name': '%s: %s' % (self.purchase_id.name, self.picking_id.name),
            'product_id': line.product_id.id,
            'product_uom_id': line.product_uom.id,
            'quantity': line.move_id.quantity_done,
            'tax_ids': [(6, 0, line.purchase_line_id.taxes_id.ids)],
            'price_unit': self.purchase_id.currency_id._convert(line.purchase_line_id.price_unit, aml_currency, self.purchase_id.company_id, date, round=False),
            'purchase_line_id': line.purchase_line_id.id,
            'picking_line_id': line.move_id and line.move_id.id or False
        }
        if not line:
            return res

        return res


class StockPickingValidateLines(models.TransientModel):
    _name = 'stock.picking.validate.lines'
    _description = 'Stock Picking Validate Lines'

    product_id = fields.Many2one('product.product', string="Product")
    purchase_line_id = fields.Many2one('purchase.order.line', string='Purchase Line')
    product_uom = fields.Many2one('uom.uom')
    quantity = fields.Float(string='Actual Qty')
    wiz_id = fields.Many2one('stock.picking.validate')
    move_id = fields.Many2one('stock.move')
    transfer_move_id = fields.Many2one('stock.move')
    receiving_qty = fields.Float(string='Receiving Qty')
    batch_number = fields.Char(string='Batch No', size=10)
    warehouse_id = fields.Many2one('stock.warehouse', string='Location')
    expiry_date = fields.Date(string="Expiry Date")
    lot_id = fields.Many2one('stock.production.lot', string="Lot")
    
    
    @api.constrains('receiving_qty')
    def check_receiving_qty(self):
        for rec in self:
            if rec.receiving_qty > rec.quantity:
                raise ValidationError(_('Receiving qty cannot be greater than actual qty'))
                

    @api.constrains('expiry_date')
    def check_expiry_date(self):
        for rec in self:
            today = fields.Date.context_today(self)
            if rec.expiry_date:
                if rec.expiry_date < today:
                    raise ValidationError(_('Expiry date cannot be past date'))

    def get_lot_name(self, move_line):
        for rec in self:
            new_defaultcode = ''.join(char for char in rec.product_id.default_code if char.isalnum())
            defaultcode = new_defaultcode.lstrip('0')
            if rec.batch_number:
                barcode_prefix = rec.batch_number.upper() + str(defaultcode[:3]).upper()
            else:
                barcode_prefix = str(defaultcode[:3]).upper()
            lot_name = barcode_prefix + str(move_line.id)
            lot_name = ''.join(c for c in lot_name if c.isalnum()).upper()
            return lot_name


