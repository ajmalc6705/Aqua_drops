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

    warehouse_id = fields.Many2one('stock.warehouse', string="Branch", domain=_get_warehouse_domain,
                                   default=_get_warehouse)
    is_branch_readonly = fields.Boolean(string="Branch Visibility", default=_get_is_branch_readonly)
    aqua_sale_type = fields.Selection([('internal', 'Internal'), ('coupon', 'Coupon')], default='internal',
                                      string="Sale Type")
    is_aqua_sale = fields.Boolean(string="Is aqua sale")

    @api.onchange('aqua_sale_type')
    def onchange_order_line(self):
        for rec in self:
            rec.order_line = False

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for rec in self:
            if rec.aqua_sale_type == 'coupon':
                for line in rec.order_line:
                    for coupon in line.coupon_ids:
                        coupon.status = "used"
            if rec.picking_ids:
                for picking in rec.picking_ids:
                    picking.is_aqua_sale_picking = True
            # pickings_to_validate = rec.picking_ids and rec.picking_ids.filtered(lambda p: p.state in ['assigned']) or False
            # if pickings_to_validate and len(pickings_to_validate.ids)==1:
            #     pickings_to_validate.button_validate()
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    coupon_ids = fields.Many2many('aqua.customer.coupon.lines', 'sale_order_line_coupon_line_rel', 'sale_line_id',
                                  'coupon_line_id', string="Coupon")

    @api.onchange('coupon_ids')
    def onchange_coupon_ids(self):
        for rec in self:
            product_uom_qty = 0
            if rec.coupon_ids:
                product_uom_qty = len(rec.coupon_ids.ids) or 0
            rec.product_uom_qty = product_uom_qty

    @api.constrains('price_unit')
    def check_price_unit_orderline(self):
        for rec in self:
            if rec.price_unit < 0:
                raise ValidationError(_("Unit price must be positive for the product '%s'" % str(rec.product_id.name)))
            else:
                rec.price_unit = rec.product_id.list_price
                