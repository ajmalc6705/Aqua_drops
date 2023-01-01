from odoo import api, fields, models, _


class ResPartner(models.Model):
  
    _inherit = "res.partner"

    sale_due_amount = fields.Float(string="Due Amount",compute='compute_sale_bils')
    sale_bill_count = fields.Integer(string="Sale bills count",compute='compute_sale_bils')
    
    # @api.depends('account_move_ids','account_move_ids.move_type','account_move_ids.is_aqua_sale_bill','account_move_ids.amount_residual')
    def compute_sale_bils(self):
        for rec in self:
            account_move_ids = []
            amount = 0
            count = 0
            for line in rec.account_move_ids:
                if line.is_aqua_sale_bill and line.move_type=='out_invoice':
                    count+= 1
                    amount += line.amount_residual
            rec.sale_due_amount = amount
            rec.sale_bill_count = count
                    

    def action_view_sale_invoice(self):
        for rec in self:
            account_move_ids = []
            for line in rec.account_move_ids:
                if line.is_aqua_sale_bill and line.move_type=='out_invoice':
                    account_move_ids.append(line.id)
            if account_move_ids!=[]:
                form_view_id = self.env.ref('aqua_sale_customization.aqua_sale_account_move_form_view').id or False
                tree_view_id = self.env.ref('aqua_sale_customization.aqua_sale_account_move_tree_view').id or False
                return {
                    'name': _('Sale Bills'),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                    'res_model': 'account.move',
                    'type': 'ir.actions.act_window',
                    'domain': [('id', 'in', account_move_ids or [])],
                    'target': 'current',
                    'context':{'create': False,'edit': False,'delete':False}
                }
            