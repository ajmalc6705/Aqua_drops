from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    def _get_warehouse_domain(self):
        loged_user = self.env.user
        current_branch_ids = []
        if loged_user and loged_user.branch_ids:
            current_branch_ids = loged_user.branch_ids.ids
        return [('id', 'in', current_branch_ids)]

    warehouse_id = fields.Many2one('stock.warehouse',string="Branch",domain=_get_warehouse_domain)
    aqua_sale_type = fields.Selection([('internal','Sales Invoice'),('coupon','Coupon')],default='internal',string="Sale Type")
    is_aqua_sale = fields.Boolean(string="Is aqua sale")
    sale_bills_count = fields.Integer(string="Bills Count",compute='compute_sale_bills_count')

    def compute_sale_bills_count(self):
        for rec in self:
            account_move_ids = self.env['account.move'].search([('aqua_sale_id','=',rec.id),('is_aqua_sale_bill','=',True)])
            rec.sale_bills_count = account_move_ids and len(account_move_ids.ids) or 0

    def action_view_sale_invoice(self):
        for rec in self:
            account_move_ids = self.env['account.move'].search([('aqua_sale_id','=',rec.id),('is_aqua_sale_bill','=',True)])
            if account_move_ids:
                form_view_id = self.env.ref('aqua_sale_customization.aqua_sale_account_move_form_view').id or False
                tree_view_id = self.env.ref('aqua_sale_customization.aqua_sale_account_move_tree_view').id or False
                return {
                    'name': _('Bills'),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                    'res_model': 'account.move',
                    'type': 'ir.actions.act_window',
                    'domain': [('id', 'in', account_move_ids.ids or [])],
                    'target': 'current',
                    'context':{'create': False,'edit': False,'delete':False}
                }

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.is_aqua_sale:
            self.warehouse_id = False
            # self.warehouse_id = self.warehouse_id and self.warehouse_id.id or False
        else:
            return super(SaleOrder, self)._onchange_company_id()

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
        for rec in self:
            # picking_id = picking.create({
            #     'location_dest_id': self.env.ref('stock.stock_location_customers').id,
            #     'location_id': rec.warehouse_id.int_type_id.default_location_src_id.id,
            #     'picking_type_id': rec.warehouse_id.out_type_id.id,
            #     'warehouse_id': self.warehouse_id and self.warehouse_id.id or False,
            #     'origin': str(rec.name),
            #     'partner_id': rec.partner_id.id,
            #     'is_aqua_sale_picking': True,
            #     'aqua_sale_id': rec.id
            #     })
            # picking_id.action_confirm()
            # for line in rec.order_line:
            #     move_id = move_pool.create({
            #         'location_dest_id': self.env.ref('stock.stock_location_customers').id,
            #         'location_id': rec.warehouse_id.int_type_id.default_location_src_id.id,
            #         'product_id': line.product_id.id or False,
            #         'product_uom_qty': line.product_uom_qty or False,
            #         'product_uom': line.product_uom.id or False,
            #         'picking_type_id': rec.warehouse_id.out_type_id.id,
            #         'origin': rec.name,
            #         'name': rec.name + " - " + line.product_id.name,
            #         'sale_line_id':line.id,
            #         'picking_id':picking_id.id
            #     })
            #
            # for mv in picking_id.move_lines:
            #     if mv.product_uom:
            #         product_uom_id = mv.product_uom.id
            #     else:
            #         product_uom_id = mv.product_id.uom_id.id
            #     mv.move_line_ids = [(0,0,{'picking_id': picking_id.id,
            #                               'location_id': mv.location_id and mv.location_id.id or False,
            #                                'location_dest_id': mv.location_dest_id and mv.location_dest_id.id or False,
            #                                'product_uom_qty':mv.product_uom_qty,
            #                                'product_uom_id': product_uom_id,
            #                                'product_id': mv.product_id and mv.product_id.id or False,
            #                               'move_id': mv.id
            #                               })]
            #
            #     if len(mv.move_line_ids) > 1:
            #         for mv_line in mv.move_line_ids[1:]:
            #             mv_line.unlink()
            # picking_id.action_assign()
            rec.action_confirm()
            for picking in rec.picking_ids:
                picking.write({'warehouse_id': self.warehouse_id and self.warehouse_id.id or False,
                               'is_aqua_sale_picking': True,
                               'aqua_sale_id': rec.id
                               })
            if rec.aqua_sale_type == 'coupon':
                for line in rec.order_line:
                    for coupon in line.coupon_ids:
                        if coupon.status == 'used':
                            raise ValidationError(_("Coupon %s does not available"%(str(coupon.sl_no))))
                        else:
                            coupon.status = "used"
            rec.state = 'sale'

    def _get_action_view_picking(self, pickings):
        if self.is_aqua_sale:
            action = self.env["ir.actions.actions"]._for_xml_id("aqua_sale_customization.action_aqua_water_delivery")
    
            if len(pickings) > 1:
                action['domain'] = [('id', 'in', pickings.ids)]
            elif pickings:
                form_view = [(self.env.ref('aqua_sale_customization.aqua_water_delivery_form_view').id, 'form')]
                if 'views' in action:
                    action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
                else:
                    action['views'] = form_view
                action['res_id'] = pickings.id
            # Prepare the context.
            picking_id = pickings.filtered(lambda l: l.picking_type_id.code == 'outgoing')
            if picking_id:
                picking_id = picking_id[0]
            else:
                picking_id = pickings[0]
            action['context'] = dict(self._context, default_partner_id=self.partner_id.id, default_picking_type_id=picking_id.picking_type_id.id, default_origin=self.name, default_group_id=picking_id.group_id.id)
            return action
        else:
            return super()._get_action_view_picking(pickings)

            
class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    
    coupon_ids = fields.Many2many('aqua.customer.coupon.lines','sale_order_line_coupon_line_rel','sale_line_id','coupon_line_id',string="Coupon")
    
    @api.onchange('coupon_ids','product_id')
    def onchange_coupon_ids(self):
        for rec in self:
            if rec.order_id: 
                if rec.order_id.aqua_sale_type == 'coupon':
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
                else:
                    rec.price_unit = rec.product_id and rec.product_id.lst_price or 0
                    
            
    @api.constrains('price_unit')
    def check_price_unit(self):
        for rec in self:
            if rec.price_unit < 0:
                raise ValidationError(_("Unit price must be positive for the product '%s'"% str(rec.product_id.name)))
                
