# Implementation Plan — helpdesk-community v1.0.0

> Golden SPEC frozen. No feature changes during implementation.

## Order

Security → Models → Sequences → Menus → Actions → Views → Portal → Notifications → Demo Data → Tests → Documentation

## Sprints

### Sprint 1 — Security + Models + Sequences

| Task | Files | Compiler? |
|------|-------|-----------|
| Groups: group_user, group_team_leader, group_manager | `security/helpdesk_groups.xml` | ✅ |
| Record rules: team-level, portal-level | `security/helpdesk_security.xml` | ✅ |
| Model: helpdesk.ticket | `models/helpdesk_ticket.py` | ✅ |
| Model: helpdesk.stage | `models/helpdesk_stage.py` | ✅ |
| Model: helpdesk.team | `models/helpdesk_team.py` | ✅ |
| Model: helpdesk.category | `models/helpdesk_category.py` | ✅ |
| Model __init__ | `models/__init__.py` | ✅ |
| Module __init__ | `__init__.py` | ✅ |
| Manifest | `__manifest__.py` | ✅ |
| ir.model.access.csv | `security/ir.model.access.csv` | ✅ |
| Sequence: ticket_number (HD00001) | `data/helpdesk_sequence.xml` | ✅ |
| ACL: all models | `security/ir.model.access.csv` | ✅ |

### Sprint 2 — Menus + Actions + Views

| Task | Files | Compiler? |
|------|-------|-----------|
| Menu items | `views/helpdesk_menu.xml` | ✅ |
| Window actions | `views/helpdesk_actions.xml` | ✅ |
| Ticket tree view | `views/helpdesk_ticket_views.xml` | ✅ |
| Ticket form view | `views/helpdesk_ticket_views.xml` | ✅ |
| Ticket kanban view | `views/helpdesk_ticket_kanban.xml` | ✅ |
| Ticket search view | `views/helpdesk_ticket_views.xml` | ✅ |
| Stage tree + form | `views/helpdesk_stage_views.xml` | ✅ |
| Team tree + form | `views/helpdesk_team_views.xml` | ✅ |
| Category tree + form | `views/helpdesk_category_views.xml` | ✅ |

### Sprint 3 — Portal + Notifications

| Task | Files | Compiler? |
|------|-------|-----------|
| Portal controller | `controllers/portal.py` | ❌ (custom) |
| Portal ticket list template | `views/portal_ticket_templates.xml` | ❌ |
| Portal ticket form template | `views/portal_ticket_templates.xml` | ❌ |
| Email notification templates | `data/mail_templates.xml` | ❌ |
| Wire mail.thread on ticket | `models/helpdesk_ticket.py` | ❌ |

### Sprint 4 — Tests + Demo Data

| Task | Files | Compiler? |
|------|-------|-----------|
| Demo: stages (New / IP / Resolved / Closed) | `demo/helpdesk_demo.xml` | ✅ (partial) |
| Demo: team + members | `demo/helpdesk_demo.xml` | ✅ |
| Demo: categories | `demo/helpdesk_demo.xml` | ✅ |
| Demo: sample tickets | `demo/helpdesk_demo.xml` | ✅ |
| Unit: test model creation | `tests/test_helpdesk_models.py` | ✅ (skeleton) |
| Unit: test workflow transitions | `tests/test_helpdesk_workflow.py` | ❌ |
| Unit: test portal access | `tests/test_helpdesk_portal.py` | ❌ |
| Unit: test security rules | `tests/test_helpdesk_security.py` | ❌ |

### Sprint 5 — Documentation + Packaging

| Task | Files | Compiler? |
|------|-------|-----------|
| README.md | `README.md` | ❌ (custom) |
| CHANGELOG.md | `CHANGELOG.md` | ❌ |
| DESCRIPTION.html | `static/description/DESCRIPTION.html` | ❌ |
| FAQ.md | `docs/FAQ.md` | ❌ |
| SUPPORT.md | `docs/SUPPORT.md` | ❌ |
| Screenshots | `static/description/screenshot_*.png` | ❌ |
| Odoo store icon | `static/description/icon.png` | ❌ |

## Compiler usage

All items marked "✅" in the Compiler? column should be generated via OdooGen (Tier A `generate_module`). Manual edits are applied only where the compiler output needs business logic or UX polish.

## Acceptance gate

Ship only when all 14 Acceptance Criteria from SPEC.md pass.
