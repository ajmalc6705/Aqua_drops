from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class StockPicking(models.Model):
  
    _inherit = "stock.picking"
    _order = 'id desc, scheduled_date desc'
    
    is_aqua_sale_picking = fields.Boolean(string="Is aqua sale picking")
    aqua_sale_id = fields.Many2one('sale.order', string="Sale")

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        for rec in self:
            if rec.is_aqua_sale_picking:
                if rec.state == 'done':
                    rec.aqua_action_create_sale_invoice()
        return res

    def _aqua_sale_prepare_invoice(self, sale,journal):
        self.ensure_one()
        move_type = self._context.get('default_move_type', 'out_invoice')
        journal = self.env['account.move'].with_context(default_move_type=move_type)._get_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting purchase journal for the company %s (%s).') % (self.company_id.name, self.company_id.id))
        picking_id = self.id
        invoice_vals = {
            'ref': '',
            'move_type': move_type,
            'currency_id': sale.currency_id.id,
            'invoice_user_id': self.env.user.id,
            'partner_id': sale.partner_id.id,
            'fiscal_position_id': (sale.fiscal_position_id or sale.fiscal_position_id.get_fiscal_position(sale.partner_id.id)).id,
            'invoice_origin': sale.name or '' + '/',
            'invoice_line_ids': [],
            'company_id': sale.company_id.id,
            'picking_id': picking_id,
            'invoice_date': sale.date_order,
            'journal_id': journal and journal.id,
            'is_aqua_sale_bill':True,
            'warehouse_id':sale.warehouse_id and sale.warehouse_id.id or False,
            'aqua_sale_id':sale.id
        }
        return invoice_vals

    def aqua_action_create_sale_invoice(self):
        sale = self.aqua_sale_id
        sequence = 1
        move_type = self._context.get('default_move_type', 'out_invoice')
        journal = self.env['account.move'].with_context(default_move_type=move_type)._get_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting purchase journal for the company %s (%s).') % (self.company_id.name, self.company_id.id))
        
        invoice_vals = self._aqua_sale_prepare_invoice(sale,journal)
        picking_id = self
        for line in self.move_ids_without_package:
            line_vals = self._prepare_aqua_sale_account_move_line(line, picking_id,journal)
            line_vals.update({'sequence': sequence})
            invoice_vals['invoice_line_ids'].append((0, 0, line_vals))
            sequence += 1

        if invoice_vals:
            AccountMove = self.env['account.move'].with_context(default_move_type='out_invoice')
            invoice_id = AccountMove.create(invoice_vals)
            invoice_id.action_post()
            picking_id.write({'invoice_id': invoice_id.id})

    def _prepare_aqua_sale_account_move_line(self, line=False, picking_id=False,journal=False):
        account_id = journal.default_account_id
        if not account_id:
            raise ValidationError("Expense Account not configured")
        aml_currency = self.aqua_sale_id and self.aqua_sale_id.currency_id
        date = fields.Date.today()
        res = {}
        if line.quantity_done>0:
            res = {
                'name': '%s: %s' % (self.aqua_sale_id.name, picking_id.name),
                'product_id': line.product_id.id,
                'product_uom_id': line.sale_line_id.product_uom.id,
                'quantity': line.quantity_done,
                'tax_ids': [(6, 0, line.sale_line_id.tax_id.ids)],
                'price_unit': self.aqua_sale_id.currency_id._convert(line.sale_line_id.price_unit, aml_currency, self.aqua_sale_id.company_id, date, round=False),
                'account_id': account_id.id,
            }
        if not line:
            return res
    
        return res
