# Helpdesk Community — SPEC

> Helpdesk / Support Ticket Management for Odoo 19.0
> License: LGPL-3.0 | Open-core: Community edition

---

## 1. Scope

### 1.1 In scope (Community)

| Feature | Description |
|---------|-------------|
| Tickets | Create, edit, close support tickets (subject, description, priority) |
| Stages | Customizable pipeline: New → In Progress → Resolved → Closed |
| Teams | Group agents into helpdesk teams |
| Assignees | Assign tickets to specific team members |
| Categories | Categorize tickets by type / product / department |
| Customer Portal | Portal users can view and create tickets |
| Email Notifications | Notify assignee and customer on ticket state changes |
| Kanban View | Drag-and-drop ticket pipeline |
| Search / Filter | Full search, filter by stage/team/priority/assignee |
| Access Control | Separate permissions for agent, team leader, portal user |

### 1.2 Out of scope (reserved for Pro)

| Feature | Reason |
|---------|--------|
| SLA management | Advanced logic, needs Pro license |
| Email gateway (inbound) | Requires mail server config, Pro feature |
| Automated triggers / actions | Workflow automation, Pro |
| Advanced dashboards / reports | BI layer, Pro |
| Time tracking on tickets | Integration with hr_timesheet, Pro |
| Canned responses / KB | Knowledge base, Pro |
| Multi-company | Enterprise feature, Pro |

### 1.3 Odoo Dependencies

- `base` (always)
- `mail` (notifications)
- `portal` (customer access)
- `web` (kanban views)

No external services or API keys required.

---

## 2. Data Model

### 2.1 `helpdesk.ticket`

| Field | Type | Notes |
|-------|------|-------|
| name | Char | Ticket subject, required |
| description | Html | Ticket body |
| priority | Selection | Low / Medium / High / Urgent |
| stage_id | Many2one → helpdesk.stage | Current stage |
| team_id | Many2one → helpdesk.team | Assigned team |
| user_id | Many2one → res.users | Assigned agent |
| category_id | Many2one → helpdesk.category | Ticket category |
| partner_id | Many2one → res.partner | Customer (creator) |
| active | Boolean | Archive |
| close_date | Datetime | When resolved → closed |
| create_date | Datetime | Auto-set by Odoo |

### 2.2 `helpdesk.stage`

| Field | Type | Notes |
|-------|------|-------|
| name | Char | Stage name |
| sequence | Integer | Pipeline order |
| fold | Boolean | Fold in kanban (closed stages) |
| team_ids | Many2many → helpdesk.team | Restrict to teams (optional) |

### 2.3 `helpdesk.team`

| Field | Type | Notes |
|-------|------|-------|
| name | Char | Team name |
| member_ids | Many2many → res.users | Team members |
| assign_method | Selection | Manual / Random (future: auto) |

### 2.4 `helpdesk.category`

| Field | Type | Notes |
|-------|------|-------|
| name | Char | Category name |
| team_id | Many2one → helpdesk.team | Default team |
| active | Boolean | |

---

## 3. Views

| View | Type | Audience |
|------|------|----------|
| Ticket tree | List | Agents |
| Ticket form | Form | Agents |
| Ticket kanban | Kanban | Agents |
| Ticket search | Search | Agents |
| Team tree | List | Admins |
| Team form | Form | Admins |
| Stage tree | List | Admins |
| Stage form | Form | Admins |
| Category tree | List | Admins |
| Category form | Form | Admins |
| Portal ticket list | List | Customers |
| Portal ticket form | Form | Customers |

---

## 4. Security

| Group | Access |
|-------|--------|
| helpdesk.group_user | Read / write own tickets |
| helpdesk.group_team_leader | Read / write team tickets, manage stages/categories |
| helpdesk.group_manager | Full access, manage teams |
| portal | Read / create own tickets (portal restricted) |

Record rules:
- Users see only their team's tickets (unless manager)
- Portal users see only their own tickets

---

## 5. Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| Odoo version | 19.0 Community & Enterprise |
| Python | 3.10+ |
| Performance | < 200ms for ticket list with 10k records |
| i18n | English + Vietnamese (vi) |
| Tests | Unit tests for all models, coverage > 80% |
| CI | Manifest check, lint, test on push to main/develop |

---

## 6. Release Criteria

| Check | Required |
|-------|----------|
| All tests pass | ✅ |
| No critical lint errors | ✅ |
| README + CHANGELOG updated | ✅ |
| Screenshots in `static/description/` | ✅ |
| `__manifest__.py` complete | ✅ |
| Demo data works | ✅ |
| Portal access tested | ✅ |
| Odoo App Store listing ready | ✅ |

---

## 7. Future (Post v1.0)

- Email gateway (Pro)
- SLA timers (Pro)
- Automated assignments (Pro)
- Reporting dashboard (Pro)
- Knowledge base / canned responses (Pro)
- Multi-language translations
