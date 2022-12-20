from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class ShipmentReceiveWiz(models.TransientModel):
    _name = 'shipment.receive.wiz'
    _description = 'Receive Shipment'
    
    @api.model
    def default_get(self, fields):
        res = super(ShipmentReceiveWiz, self).default_get(fields)
        picking = False
        if self._context.get('active_model') == 'stock.picking' and self._context.get('active_id'):
            picking = self.env['stock.picking'].browse(self._context.get('active_id'))
            if picking:
                res.update({
                    'purchase_id': picking and picking.purchase_id and picking.purchase_id.id or False,
                    'picking_id':picking and picking.id or False,
                })
        return res

    @api.model
    def get_wiz_line(self):
        lines = []
        if self._context.get('active_model') == 'stock.picking' and self._context.get('active_id'):
            picking = self.env['stock.picking'].browse(self._context.get('active_id'))
            wiz_line_pool = self.env['shipment.receive.wiz.lines']
        
            if picking:
                for line in picking.move_ids_without_package.filtered(lambda i: i.pending_qty > 0.0):
                    line = wiz_line_pool.create({
                        'product_id': line.product_id and line.product_id.id or False,
                        'purchase_line_id': line.purchase_line_id and line.purchase_line_id.id or False,
                        'quantity': line.pending_qty or 0.0,
                        'move_id':line.id or False,
                        'expiry_date':line.expiry_date
                    })
                    lines.append(line.id)
        return lines
    
    wiz_line_ids = fields.One2many('shipment.receive.wiz.lines','wiz_id',string="Products",default=get_wiz_line)
    picking_id = fields.Many2one('stock.picking',string="Picking")
    purchase_id = fields.Many2one('purchase.order',string="Purchase")
    
    def proceed_picking_action(self):
        lot_pool = self.env['stock.production.lot']
        for rec in self:
            move_line_dict = {}
            picking = rec.picking_id
            for line in rec.wiz_line_ids.filtered(lambda i: i.quantity > 0):
                if not line.expiry_date:
                    raise ValidationError(_('Please update expiry date.'))
                if not line.batch:
                    raise ValidationError(_('Please update batch.'))
                if line.quantity>line.move_id.pending_qty:
                    raise ValidationError(_('Qty cannot be greater than pending qty.'))
                lot_pool.check_duplicate_batch_number(line.product_id.id, line.batch.upper())
                for picking_move in picking.move_lines:
                    if picking_move.product_id == line.product_id and picking_move.purchase_line_id == line.purchase_line_id:
                        old_move_line = picking_move.move_line_ids[0]
                        
                taxes = line.purchase_line_id and line.purchase_line_id.taxes_id  and line.purchase_line_id.taxes_id.ids or []
                move_line = old_move_line.copy()
                move_line.product_uom_qty = line.quantity
                lot_name = rec.create_barcode(line, move_line)
                print("=========================purchase_line_id",line.purchase_line_id.company_id,line.purchase_line_id.company_id.id)
                lot_id = lot_pool.create({
                    'name': lot_name,
                    'product_id': move_line.product_id.id,
                    'partner_id': rec.purchase_id and rec.purchase_id.partner_id and rec.purchase_id.partner_id.id or False,
                    'unit_price': line.purchase_line_id.price_unit or 0.00,
                    'purchase_line_id': line.purchase_line_id.id,
                    'location_id': picking.location_dest_id.id,
                    'batch_number': line.batch,
                    'warehouse_id':rec.purchase_id.warehouse_id.id or False,
                    'taxes_ids': [(6,0,taxes or [])],
                    'expiry_date':line.expiry_date,
                    # 'company_id':line.purchase_line_id.company_id or line.purchase_line_id.company_id.id or False
                    'company_id':1
                })
                move_line.lot_id = lot_id.id
                move_line.qty_done = move_line.product_uom_qty
                line.lot_ids = [(4,lot_id.id)]
                old_move_line.unlink()
            
            if picking._check_backorder():
                back_order = self.env['stock.backorder.confirmation'].create(
                    {'pick_ids': [(4, p.id) for p in picking]})
                back_order.process()
                next_picking = self.env['stock.picking'].search([('backorder_id','=',picking.id)],limit=1)
                print("======11111111========",next_picking,picking)
                if next_picking:
                    next_picking.is_aqua_picking = True
            else:
                picking.action_done()                    
                                    
            for line in rec.wiz_line_ids.filtered(lambda i: i.quantity > 0): 
                lot_id = line.lot_ids.filtered(lambda i: not i.is_aqua_lot)[0]
                move = self.env['stock.move'].create({
                            'name': "Receive : %s" % rec.purchase_id.name,
                            'origin': rec.purchase_id.name,
                            'product_id': line.product_id.id,
                            'product_uom': line.purchase_line_id.product_uom.id or False,
                            'product_uom_qty': line.quantity,
                            'location_id': picking.location_dest_id and picking.location_dest_id.id or False,
                            'location_dest_id': rec.purchase_id.warehouse_id and rec.purchase_id.warehouse_id.int_type_id and rec.purchase_id.warehouse_id.int_type_id.default_location_dest_id and rec.purchase_id.warehouse_id.int_type_id.default_location_dest_id.id,
                        })
                move._action_confirm(merge=False)
                move._action_assign()
                if move.move_line_ids:
                    move.move_line_ids.write({
                        'purchase_line_id':line.purchase_line_id and line.purchase_line_id.id or False
                    })
                    move_line_id = move.move_line_ids and move.move_line_ids[0]
                    move_line_id.lot_id = lot_id.id
                    move_line_id.location_id = picking.location_dest_id.id
                    move_line_id.qty_done = line.quantity
                    for move_line in move.move_line_ids[1:]:
                        move_line.unlink()
                else:
                    vals = {
                        'move_id': move.id,
                        'product_id': move.product_id.id,
                        'product_uom_id': move.product_uom.id,
                        'location_id': move.location_id.id,
                        'location_dest_id': move.location_dest_id.id,
                        'lot_id': lot_id.id,
                        'purchase_line_id':line.purchase_line_id and line.purchase_line_id.id or False
                    }
                    move_line_id = self.env['stock.move.line'].create(vals)
                    move_line_id.lot_id = lot_id.id
                    move_line_id.qty_done = line.quantity
                
                move._action_done()
                lot_id.write({
                    'is_aqua_lot': True,
                    'location_id': rec.purchase_id.warehouse_id and rec.purchase_id.warehouse_id.int_type_id and rec.purchase_id.warehouse_id.int_type_id.default_location_dest_id and rec.purchase_id.warehouse_id.int_type_id.default_location_dest_id.id,
                    'warehouse_id': rec.purchase_id.warehouse_id.id or False
                })

    def create_barcode(self,line, move_line):
        for rec in self:
            new_defaultcode = ''.join(char for char in line.product_id.default_code if char.isalnum())
            defaultcode = new_defaultcode.lstrip('0')
            barcode_prefix = line.batch.upper() + str(defaultcode[:3]).upper() 
            lot_name = barcode_prefix + str(move_line.id)
            lot_name =  ''.join(c for c in lot_name if c.isalnum()).upper()
            return lot_name
            

class ShipmentReceiveWizLines(models.TransientModel):
    _name = 'shipment.receive.wiz.lines'
    _description = 'Receive Shipment Lines'
    
    wiz_id = fields.Many2one('shipment.receive.wiz',string="Shipment wiz")
    product_id = fields.Many2one('product.product')
    purchase_line_id = fields.Many2one('purchase.order.line')
    move_id = fields.Many2one('stock.move')
    batch = fields.Char(string="Batch",size=10)
    quantity = fields.Float(string="Qty")
    expiry_date = fields.Date(string="Expiry Date")
    lot_ids = fields.Many2many('stock.production.lot', 'shipment_receive_wiz_lines_stock_lot_rel',
                              'shipment_receive_wiz_lines_id', 'lot_id', string='Barcode')
    

