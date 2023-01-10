from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class StockPicking(models.Model):
  
    _inherit = "stock.picking"
    _order = 'id desc'
    
    po_attachment = fields.Binary(string='Attachment', attachment=True)
    po_file_name = fields.Char(string="File name")
    document_number = fields.Char(string="Document Number")
    
    def aqua_action_receive_shipment(self):
        for rec in self:
            context = self._context.copy()
            picking_id = None
            if rec.state == 'assigned':
                picking_id = rec.id
    
            context.update({
                'active_model': 'stock.picking',
                'active_id': picking_id,
                'active_ids': [picking_id]
            })
            return_vals = {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'res_model': 'stock.picking.validate',
                'view_id':self.env.ref('aqua_purchase_customization.aqua_stock_picking_validate').id,
                'context': context
            }
            return return_vals


    def action_view_shipment_invoice(self):
        for rec in self:
            if rec.invoice_id:
                form_view_id = self.env.ref('aqua_purchase_customization.aqua_po_account_move_form_view').id or False
                tree_view_id = self.env.ref('aqua_purchase_customization.aqua_po_account_move_tree_view').id or False
                return {
                    'name': _('Vendor Bills'),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                    'res_model': 'account.move',
                    'type': 'ir.actions.act_window',
                    'domain': [('id', '=',rec.invoice_id.id)],
                    'target': 'current',
                    'context':{'create': False,'edit': False,'delete':False}
                }

    def action_view_po(self):
        for rec in self:
            if rec.purchase_id:
                form_view_id = self.env.ref('aqua_purchase_customization.aqua_water_purchase_form_view').id or False
                tree_view_id = self.env.ref('aqua_purchase_customization.aqua_water_purchase_tree_view').id or False
                return {
                    'name': _('Purchase Order'),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                    'res_model': 'purchase.order',
                    'type': 'ir.actions.act_window',
                    'domain': [('id', '=',rec.purchase_id.id)],
                    'target': 'current',
                    'context':{'create': False,'edit': False,'delete':False}
                }
    
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
            if rec.is_aqua_picking:
                if rec.move_lines:
                    for line in rec.move_lines.move_line_ids:
                        if line.lot_id:
                            line.lot_id.expiry_date = line.move_id.expiry_date
                            line.lot_id.warehouse_id = line.move_id.warehouse_id
                            line.lot_id.location_id = rec.location_dest_id.id
                            line.lot_id.is_aqua_lot = True
                # if rec.state == 'done':
                #     rec.aqua_action_create_invoice()
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
        sequence = 1
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
            invoice_id.purchase_id = po and po.id
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