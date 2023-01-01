from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class StockPicking(models.Model):
  
    _inherit = "stock.picking"
    _order = 'id desc, scheduled_date desc'

    is_aqua_picking = fields.Boolean()
    warehouse_id = fields.Many2one('stock.warehouse', string="Branch")
    
    def button_validate(self):
        res = super(StockPicking,self).button_validate()
        for rec in self:
            if rec.is_aqua_picking:
                if rec.move_lines:
                    for line in rec.move_lines.move_line_ids:
                        if line.lot_id:
                            line.lot_id.expiry_date = line.move_id.expiry_date
                            line.lot_id.warehouse_id = line.move_id.warehouse_id
                            line.lot_id.location_id = rec.location_dest_id.id
                            line.lot_id.is_aqua_lot = True
                if rec.state == 'done':
                    rec.aqua_action_create_invoice()
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


class StockMoveLine(models.Model):
  
    _inherit = "stock.move.line"
    
    purchase_line_id = fields.Many2one('purchase.order.line')

