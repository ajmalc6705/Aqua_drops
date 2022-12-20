from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
  
    _inherit = "purchase.order"
    _description = "Aqua Purchase"

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
    aqua_po_state = fields.Selection([('draft','Draft'),('confirmed','Confirmed'),('cancelled','Cancelled')],default='draft',string="Aqua PO state")
    is_aqua_po = fields.Boolean(string="Is aqua purchase")

    @api.onchange('warehouse_id')
    def _onchange_warehouse_id(self):
        self.picking_type_id = self.warehouse_id.in_type_id.id
        
    def _prepare_picking(self):
        res = super(PurchaseOrder,self)._prepare_picking()
        res.update({'location_dest_id':self.warehouse_id and self.warehouse_id.int_type_id and self.warehouse_id.int_type_id.default_location_dest_id and self.warehouse_id.int_type_id.default_location_dest_id.id})
        return res

    def purchase_confirm(self):
        for rec in self:
            if not rec.order_line:
                raise ValidationError(_('Please add atleast one product.!'))
            if rec.aqua_po_state == 'draft':
                rec.state = 'draft'
                rec.button_confirm()
                rec.aqua_po_state = 'confirmed'
                for picking in rec.picking_ids:
                    picking.is_aqua_picking = True
                    for picking_line in picking.move_ids_without_package:
                        picking_line.expiry_date = picking_line.purchase_line_id and picking_line.purchase_line_id.expiry_date or False

    def po_cancel(self):
        for rec in self:
            if rec.aqua_po_state == 'draft':
                rec.button_cancel()
                rec.aqua_po_state = 'cancelled'
                
    def po_draft(self):
        for rec in self:
            if rec.aqua_po_state == 'cancelled':
                rec.button_draft()
                rec.aqua_po_state = 'draft'
                
class PurchaseOrderLine(models.Model):
  
    _inherit = "purchase.order.line"
    
    
    expiry_date = fields.Date(string="Expiry Date")
    
    
    @api.constrains('price_unit')
    def check_price_unit_orderline(self):
        for rec in self:
            if rec.price_unit <0:
                raise ValidationError(_("Unit price must be positive for the product '%s'"% str(rec.product_id.name)))
                
                
