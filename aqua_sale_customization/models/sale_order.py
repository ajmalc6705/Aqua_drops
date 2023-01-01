from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"
    
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
    aqua_sale_type = fields.Selection([('internal','Internal'),('coupon','Coupon')],default='internal',string="Sale Type")
    is_aqua_sale = fields.Boolean(string="Is aqua sale")

    @api.onchange('warehouse_id')
    def onchange_sale_warehouse_id(self):
        for rec in self:
            rec.partner_id = False

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        res = super(SaleOrder, self).onchange_partner_id()
        for rec in self:
            rec.order_line = False
        return res
    
    @api.onchange('aqua_sale_type')
    def onchange_order_line(self):
        for rec in self:
            rec.order_line = False
            
    def create_sale_picking(self):
        picking = self.env['stock.picking']
        move_pool = self.env['stock.move']
        picking_id = False
        for rec in self:
            picking_id = picking.create({
                'location_dest_id': self.env.ref('stock.stock_location_customers').id,
                'location_id': rec.warehouse_id.int_type_id.default_location_src_id.id,
                'picking_type_id': rec.warehouse_id.out_type_id.id,
                'origin': str(rec.name),
                'partner_id':rec.partner_id.id,
                'is_aqua_sale_picking':True,
                'aqua_sale_id':rec.id
                })
            picking_id.action_confirm()
            move_lines = []
            for line in rec.order_line:
                move_id = move_pool.create({
                    'location_dest_id': self.env.ref('stock.stock_location_customers').id,
                    'location_id': rec.warehouse_id.int_type_id.default_location_src_id.id,
                    'product_id': line.product_id.id or False,
                    'product_uom_qty': line.product_uom_qty or False,
                    'product_uom': line.product_uom.id or False,
                    'picking_type_id': rec.warehouse_id.out_type_id.id,
                    'origin': rec.name,
                    'name': rec.name + " - " + line.product_id.name,
                    'sale_line_id':line.id,
                    'picking_id':picking_id.id
                })
                
            for mv in picking_id.move_lines:
                product_uom_id = False
                if mv.product_uom:
                    product_uom_id = mv.product_uom.id
                else:
                    product_uom_id = mv.product_id.uom_id.id
                mv.move_line_ids = [(0,0,{'picking_id': picking_id.id,
                                          'location_id': mv.location_id and mv.location_id.id or False,
                                           'location_dest_id': mv.location_dest_id and mv.location_dest_id.id or False,
                                           'qty_done': mv.product_uom_qty,
                                           'product_uom_qty':mv.product_uom_qty,
                                           'product_uom_id': product_uom_id,
                                           'product_id': mv.product_id and mv.product_id.id or False
                                          })]

                if len(mv.move_line_ids) > 1:
                    for mv_line in move.move_line_ids[1:]:
                        mv_line.unlink()
            picking_id.action_assign()
            rec._action_confirm()
            if rec.aqua_sale_type == 'coupon':
                for line in rec.order_line:
                    for coupon in line.coupon_ids:
                        coupon.status = "used"
            rec.state = 'sale'

            
    # def action_confirm(self):
    #     res = super(SaleOrder, self).action_confirm()
    #
    #     for rec in self:
    #         if rec.aqua_sale_type == 'coupon':
    #             for line in rec.order_line:
    #                 for coupon in line.coupon_ids:
    #                     coupon.status = "used"
    #         if rec.picking_ids:
    #             for picking in rec.picking_ids:
    #                 picking.is_aqua_sale_picking = True
    #     return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    
    coupon_ids = fields.Many2many('aqua.customer.coupon.lines','sale_order_line_coupon_line_rel','sale_line_id','coupon_line_id',string="Coupon")
    
    @api.onchange('coupon_ids')
    def onchange_coupon_ids(self):
        for rec in self:
            product_uom_qty = 0
            price_unit = 0
            count = 0
            for line in rec.coupon_ids:
                count += 1
                price_unit += line.coupon_id and line.coupon_id.coupon_amount or 0
            if count>0:
                rec.price_unit = (price_unit/count) or 0
            product_uom_qty = rec.coupon_ids and len(rec.coupon_ids.ids) or 0
            rec.product_uom_qty = product_uom_qty
            
    @api.constrains('price_unit')
    def check_price_unit(self):
        for rec in self:
            if rec.price_unit < 0:
                raise ValidationError(_("Unit price must be positive for the product '%s'"% str(rec.product_id.name)))
                
