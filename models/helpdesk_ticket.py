from odoo import api, fields, models


class HelpdeskTicket(models.Model):
    _name = 'helpdesk.ticket'
    _description = 'Helpdesk Ticket'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string='Subject', required=True, tracking=True)
    ticket_number = fields.Char(string='Ticket Number', readonly=True, copy=False)
    description = fields.Html(string='Description')
    priority = fields.Selection(
        [('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')],
        string='Priority', default='medium', tracking=True)
    stage_id = fields.Many2one('helpdesk.stage', string='Stage',
                                required=True, tracking=True,
                                group_expand='_read_group_stage_ids')
    team_id = fields.Many2one('helpdesk.team', string='Team', tracking=True)
    user_id = fields.Many2one('res.users', string='Assigned Agent',
                               tracking=True, domain="[('share', '=', False)]")
    category_id = fields.Many2one('helpdesk.category', string='Category')
    partner_id = fields.Many2one('res.partner', string='Customer')
    active = fields.Boolean(string='Active', default=True)
    stage_change_date = fields.Datetime(string='Stage Change Date', readonly=True)
    last_activity_date = fields.Datetime(string='Last Activity Date', readonly=True)
    close_date = fields.Datetime(string='Close Date', readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('ticket_number', 'New') == 'New':
            vals['ticket_number'] = self.env['ir.sequence'].next_by_code('helpdesk.ticket') or 'New'
        if not vals.get('stage_id'):
            start_stage = self.env['helpdesk.stage'].search([('is_start', '=', True)], limit=1)
            if start_stage:
                vals['stage_id'] = start_stage.id
        res = super().create(vals)
        res.stage_change_date = fields.Datetime.now()
        res.last_activity_date = fields.Datetime.now()
        return res

    def write(self, vals):
        if 'stage_id' in vals:
            vals['stage_change_date'] = fields.Datetime.now()
        res = super().write(vals)
        if vals.get('stage_id'):
            stage = self.env['helpdesk.stage'].browse(vals['stage_id'])
            if stage.is_done and not self.close_date:
                self.write({'close_date': fields.Datetime.now()})
            elif not stage.is_done and self.close_date:
                self.write({'close_date': False})
        return res

    def action_assign(self):
        self.ensure_one()
        if not self.user_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'helpdesk.ticket',
                'view_mode': 'form',
                'res_id': self.id,
                'target': 'new',
                'context': {'default_user_id': self.env.user.id},
            }
        return True

    def action_reopen(self):
        self.write({'close_date': False})

    def action_close(self):
        self.write({'close_date': fields.Datetime.now()})

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return self.env['helpdesk.stage'].search([])
