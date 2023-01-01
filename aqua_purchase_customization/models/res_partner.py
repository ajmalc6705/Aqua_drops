from odoo import api, fields, models, _


class ResPartner(models.Model):
  
    _inherit = "res.partner"

    purchase_due_amount = fields.Float(string="Due Amount",compute='compute_po_bils')
    purchase_bill_count = fields.Integer(string="Purchase bills count",compute='compute_po_bils')
    
    @api.depends('account_move_ids','account_move_ids.move_type','account_move_ids.is_aqua_bill','account_move_ids.amount_residual')
    def compute_po_bils(self):
        for rec in self:
            amount = 0
            count = 0
            for line in rec.account_move_ids:
                if line.is_aqua_bill and line.move_type == 'in_invoice':
                    count += 1
                    amount += line.amount_residual
            rec.purchase_due_amount = amount
            rec.purchase_bill_count = count
                    
    def action_view_purchase_invoice(self):
        for rec in self:
            account_move_ids = []
            for line in rec.account_move_ids:
                if line.is_aqua_bill and line.move_type=='in_invoice':
                    account_move_ids.append(line.id)
            if account_move_ids!=[]:
                form_view_id = self.env.ref('aqua_purchase_customization.aqua_po_account_move_form_view').id or False
                tree_view_id = self.env.ref('aqua_purchase_customization.aqua_po_account_move_tree_view').id or False
                return {
                    'name': _('Purchase Bills'),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                    'res_model': 'account.move',
                    'type': 'ir.actions.act_window',
                    'domain': [('id', 'in', account_move_ids or [])],
                    'target': 'current',
                    'context':{'create': False,'edit': False,'delete':False}
                }
            