# R-ORM-002 expected <=17.0: ORM calls group_expand with a 4th `order` arg.
# Same fixture applies to 16.0, 15.0, 14.0.
    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return self.env['helpdesk.stage'].search([])
