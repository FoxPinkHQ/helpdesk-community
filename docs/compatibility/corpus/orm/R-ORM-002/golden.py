# R-ORM-002 golden (18.0 / 19.0): group_expand callback takes (self, stages, domain)
    @api.model
    def _read_group_stage_ids(self, stages, domain):
        return self.env['helpdesk.stage'].search([])
