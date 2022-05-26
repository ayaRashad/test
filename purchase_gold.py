from odoo import models, fields, api ,_
from odoo.exceptions import ValidationError, RedirectWarning, UserError
import json
class purchaseOrderGold(models.Model):
    _inherit = ["purchase.order.line"]

    lot = fields.Char(string="LOT")
    # product_template_id = fields.Many2one('product.template')
    karat_id = fields.Many2one('karat.price', related='product_id.product_tmpl_id.karat')

    price_karat = fields.Float(related='karat_id.price', string="price karat", tracking=True, store=True)
    categ_id = fields.Many2one('product.category', related='product_id.product_tmpl_id.categ_id')

    weight = fields.Float(related='product_id.product_tmpl_id.weight', string="Weight")
    product_price = fields.Float(related='product_id.product_tmpl_id.list_price', string="Gold Price")

    price_unit = fields.Float(string="price")
    labor_price_total = fields.Float(string="labor total", related='product_id.product_tmpl_id.labor_price_total')

    _sql_constraints = [
        ('lot_id_uniq', 'unique (lot)',
         "The Lot ID must be unique, this one is already assigned to another product."),
    ]

    return_lot = fields.Many2one("stock.production.lot", string="LOT")


    @api.onchange('return_lot')
    def onchange_return_lot(self):
        for record in self:
            check_lot = record.env['stock.production.lot'].search([('id', '=', record.return_lot.id)])
            if check_lot:
                if check_lot.product_id.seller_ids.name == self.partner_id:
                     self.product_id = check_lot.product_id
                else:
                    raise ValidationError(_('Warning ! you can not return purchase '))

    @api.onchange('product_template_id')
    def onchange_product_template_id(self):
        return {'domain': {'product_template_id': [('seller_ids.name', '=', self.partner_id.id)]}}

    @api.onchange('lot', 'product_qty')
    def onchange_lot(self):
        for record in self:
            check_lot = record.env['stock.production.lot'].search([('name', '=', record.lot)])
            if check_lot:
                raise ValidationError(_('Warning!'))

            elif self.product_id and self.lot:
                self.env['stock.production.lot'].create({
                    'name': self.lot,
                    'product_id': self.product_id.id,
                    'product_qty': self.product_qty,
                    'company_id': self.env.company.id})

class purchaseOrderGold(models.Model):
    _inherit = ["purchase.order"]

    return_order_line = fields.One2many('purchase.order.line', 'order_id', string='Order Lines')
    return_purchase = fields.Boolean('Return Purchase', default=False)
    karat_21 = fields.Float(string="karat 21")
    karat_18 = fields.Float(string="karat 18")
    karat_14 = fields.Float(string="karat 14")
    karat_12 = fields.Float(string="karat 12")
    karat_9 = fields.Float(string="karat 9")
    karat_24 = fields.Float(string="karat 24")
    all_labor = fields.Float(string="All Labor  ")
    all_total = fields.Float(string="All Total  ")

    to_21 = fields.Float(string=" to 21  ")

    invoice = fields.Selection([('fixed', 'Fixed'), ('daily', 'Daily')],  string="Invoice",  default='daily')

    @api.onchange('tax_totals_json', 'partner_id')
    def _compute_gold_credit_limit(self):
        data_json = json.loads(self.tax_totals_json)
        amount_total = data_json['amount_total']
        if amount_total > self.partner_id.gold_credit_limit:
            raise ValidationError(_('Warning! Total > Gold Credit Limit'))


    @api.onchange('order_line', 'invoice')
    def _compute_price_unit(self):
        for order in self:
            for product in order.order_line:
                if self.invoice == 'fixed':
                    product.price_unit = product.labor_price_total
                else:
                    product.price_unit = (product.price_karat * product.weight) + product.labor_price_total
                if self.return_purchase:
                    product.price_unit = product.price_unit * -1

    @api.onchange('order_line', 'invoice')
    def _compute_totals(self):
        price_21 = 0.0
        price_18 = 0.0
        price_14 = 0.0
        price_12 = 0.0
        price_9 = 0.0
        price_24 = 0.0
        total_labor = 0.0
        total_price = 0.0
        for order in self:
            for product in order.order_line:
                total_labor += product.labor_price_total
                total_price += product.price_subtotal

                if product.karat_id.name == 21:
                    price_21 = (price_21 + product.weight) * product.product_qty
                elif product.karat_id.name == 18:
                    price_18 = (product.weight + price_18) * product.product_qty
                elif product.karat_id.name == 14:
                    price_14 = (product.weight + price_14) * product.product_qty
                elif product.karat_id.name == 12:
                    price_12 = (product.weight + price_12) * product.product_qty
                elif product.karat_id.name == 9:
                    price_9 = (product.weight + price_9) * product.product_qty
                elif product.karat_id.name == 24:
                    price_24 = (product.weight + price_24) * product.product_qty

            self.karat_21 = price_21
            self.karat_18 = price_18
            self.karat_14 = price_14
            self.karat_12 = price_12
            self.karat_9 = price_9
            self.karat_24 = price_24
            self.to_21 = (((price_18 * 18) + (price_14 * 14) + (price_12 * 12) + (price_9 * 9) + (price_24 * 24)) / 21) + price_21
            self.all_labor = total_labor
            self.all_total = total_price



