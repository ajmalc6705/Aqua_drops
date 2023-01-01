from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


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
    latest_picking_ref = fields.Char(compute='compute_picking_ref', store=True, string="Shipment Ref")

    @api.depends('picking_ids')
    def compute_picking_ref(self):
        for rec in self:
            picking_ref = ', '.join(picking.name for picking in rec.picking_ids)
            if len(picking_ref) > 25:
                picking_ref = picking_ref[:24]
            rec.latest_picking_ref = picking_ref



    @api.model
    def _get_picking_type(self, company_id):
        res = super()._get_picking_type(company_id)
        if self.warehouse_id and self.warehouse_id.in_type_id:
            res = self.warehouse_id.in_type_id
        return res

    @api.onchange('warehouse_id')
    def _onchange_warehouse_id(self):
        self.picking_type_id = self.warehouse_id.in_type_id.id
        
    def _prepare_picking(self):
        res = super(PurchaseOrder,self)._prepare_picking()
        self.picking_type_id = self._get_picking_type(self.company_id.id)
        location_dest_id = self._get_destination_location()
        res.update({'picking_type_id': self.picking_type_id.id, 'location_dest_id': location_dest_id,
                    'warehouse_id': self.warehouse_id and self.warehouse_id.id or False})
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

    def _get_action_view_picking(self, pickings):
        if self.is_aqua_po:
            self.ensure_one()
            result = self.env["ir.actions.actions"]._for_xml_id('aqua_purchase_customization.action_aqua_water_shipment')
            # override the context to get rid of the default filtering on operation type
            result['context'] = {'default_partner_id': self.partner_id.id, 'default_origin': self.name, 'default_picking_type_id': self.picking_type_id.id}
            # choose the view_mode accordingly
            if not pickings or len(pickings) > 1:
                result['domain'] = [('id', 'in', pickings.ids)]
            elif len(pickings) == 1:
                res = self.env.ref('aqua_purchase_customization.aqua_water_shipment_form_view', False)
                form_view = [(res and res.id or False, 'form')]
                result['views'] = form_view + [(state, view) for state, view in result.get('views', []) if view != 'form']
                result['res_id'] = pickings.id
            return result
        else:
            return super()._get_action_view_picking(pickings)


class PurchaseOrderLine(models.Model):
  
    _inherit = "purchase.order.line"

    @api.model
    def default_get(self, fields_list):
        res = super(PurchaseOrderLine, self).default_get(fields_list)
        today = fields.Date.context_today(self)
        res.update({'expiry_date': today + relativedelta(years=1)})
        return res

    expiry_date = fields.Date(string="Expiry Date")
    
    @api.constrains('price_unit')
    def check_price_unit_orderline(self):
        for rec in self:
            if rec.price_unit < 0:
                raise ValidationError(_("Unit price must be positive for the product '%s'"% str(rec.product_id.name)))
                
                
