# Changelog

All notable changes to this module are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/) and this project adheres to [Semantic Versioning](https://semver.org/).

## [19.0.1.0.1] — 2026-07-13

### Fixed
- **F-001**: view/menu `groups="..."` attributes now use fully-qualified xml ids
  (`helpdesk_community.group_helpdesk_*`). Bare names failed to resolve on the
  ticket form buttons, so their group-based visibility was silently not applied.
  Odoo no longer logs "The group ... defined in view does not exist!".
- **R-ORM-002**: `_read_group_stage_ids` group_expand callback now uses the 3-arg
  signature `(self, stages, domain)` required by Odoo 18.0/19.0 (the 4-arg form
  raised `TypeError` when grouping the kanban by stage). The Compatibility Layer
  re-adds the `order` argument for Odoo ≤ 17.0.

### Added
- Regression tests: `test_13_group_expand_orm_path` (exercises group_expand via
  the real ORM path) and `test_14_security_groups_resolve` (guards F-001).

## [19.0.1.0.0] — 2026-07-13

### Added
- Initial release
- Ticket management with stages pipeline (New → In Progress → Resolved → Closed)
- Team management with configurable assignment policies
- Category management with color coding
- Customer portal for ticket creation and tracking
- Email notifications on ticket assignment and stage changes
- Kanban view with drag-and-drop support
- Three-tier access control (User / Team Leader / Manager)
- Auto-numbering with HD00000 sequence format
- Full test suite (12 unit tests)
