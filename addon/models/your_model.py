from odoo import models, fields, api


class YourModel(models.Model):
    _name = 'your.model'
    _description = 'Your Model'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='Active', default=True)
    description = fields.Text(string='Description')
