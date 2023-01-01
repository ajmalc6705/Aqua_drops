from odoo import fields, models, api
from odoo.exceptions import ValidationError,UserError


class CouponPaymentWizard(models.TransientModel):
    _name = 'coupon.payment.wizard'
    _description = 'Payment wizard'

    @api.model
    def default_get(self, default_fields):
        res = super(CouponPaymentWizard, self).default_get(default_fields)
        if self._context.get('active_model') == 'aqua.customer.coupon' and self._context.get('active_id', False):
            coupon_id = self.env['aqua.customer.coupon'].browse(self._context.get('active_id', False))
            res.update({'amount': coupon_id.amount-coupon_id.received_amount,
                        'received_amount': coupon_id.amount-coupon_id.received_amount,
                        'coupon_id':coupon_id.id})
        return res

    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    amount = fields.Monetary(string='Total Amount', required=True)
    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True, domain=[('type', 'in', ('bank', 'cash'))])
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True, copy=False)
    communication = fields.Char(string='Memo')
    received_amount = fields.Monetary(string='Received Amount', required=True)
    credit_amount = fields.Monetary(string='Credit Amount', compute='_compute_credit_amount', store=True)
    coupon_id = fields.Many2one('aqua.customer.coupon',string="Coupon")
    partner_bank_id = fields.Many2one('res.partner.bank', string="Recipient Bank Account")

    @api.depends('received_amount', 'amount')
    def _compute_credit_amount(self):
        for rec in self:
            rec.credit_amount = rec.amount - rec.received_amount


    def create_sale_payment(self):
        for rec in self:
            if rec.coupon_id:
                if not rec.amount == rec.received_amount + rec.credit_amount:
                    raise ValidationError('Credit Amount and Receive Amount should be sum of Total Amount')
                if not rec.amount == rec.coupon_id.amount-rec.coupon_id.received_amount:
                    raise ValidationError('Total Amount not matches with Total Amount')
                Payment = self.env['account.payment']
                payment = Payment.create({
                    'date':rec.payment_date,
                    'partner_bank_id': rec.partner_bank_id.id,
                    'payment_type': 'inbound',
                    'partner_type': 'customer',
                    'partner_id': rec.coupon_id.customer_id.id,
                    'amount': rec.received_amount,
                    'journal_id': rec.journal_id.id,
                    'company_id': self.env.user.company_id.id,
                    'currency_id': rec.currency_id.id,
                    'ref': rec.communication,
                    'is_aqua_coupon_payment':True
                })
                rec.coupon_id.received_amount += rec.received_amount
                rec.coupon_id.payment_ids = [(4,payment.id)]
                payment.action_post()


