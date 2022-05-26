from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class gold_karat(models.Model):
    _name = 'karat.price'
    _description = 'gold Karat'

    name = fields.Integer('Karat')
    price = fields.Float('Price')
    active_from_date = fields.Date('Active From Date', help="Start date ", default=fields.Date.context_today)
    main_karat = fields.Boolean('Main Karat', default=True)

    @api.model
    @api.onchange('price', 'main_karat')
    def _calculated_price(self):
        for id_main in self:
            if (id_main.main_karat == True):
                update_main_karat_price = id_main.price or 1
                update_main_karat_name = id_main.name or 1
            else:
                raise ValidationError(_('Warning! This karat must be a main karat to be able to modify it.'))

        not_main_karat_list = self.search([('main_karat', '=', False)])

        for karat in not_main_karat_list:
            karat.price = (karat.name / update_main_karat_name) * update_main_karat_price
        return {
            'type': 'ir.actions.client',
            'tag': 'reload'}

    @api.model
    @api.onchange('main_karat')
    def _close_main_karat(self):
        main_karat_list = self.search([('main_karat', '=', True)])
        for m in main_karat_list:
            m.main_karat = False
        return {
            'type': 'ir.actions.client',
            'tag': 'reload'}





