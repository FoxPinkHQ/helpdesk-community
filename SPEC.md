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

## 2. Workflow

### 2.1 Stage Transitions

```
                     ┌─────────────────┐
                     │      New        │
                     └────────┬────────┘
                              │ Assign
                              ▼
                     ┌─────────────────┐
                     │  In Progress    │
                     └────────┬────────┘
                              │ Resolve
                              ▼
                     ┌─────────────────┐
                     │    Resolved     │◄──────── Reopen ──────────┐
                     └────────┬────────┘                          │
                              │ Close                             │
                              ▼                                   │
                     ┌─────────────────┐                          │
                     │     Closed      ├──── Reopen (Manager) ─────┘
                     └─────────────────┘
```

### 2.2 Transition Rules

| From | To | Condition | Note |
|------|----|-----------|------|
| New | In Progress | Assignee set | Auto via Assign action |
| In Progress | Resolved | Agent resolves | Sets resolve_date |
| Resolved | Closed | Agent or Manager closes | Sets close_date |
| Resolved | In Progress | Reopen | Clears close_date |
| Closed | In Progress | Manager only | Reopen archived ticket |
| New | Closed | Not allowed | Must go through pipeline |

Closed tickets are read-only for non-Managers.

---

## 3. Data Model

### 3.1 `helpdesk.ticket`

| Field | Type | Notes |
|-------|------|-------|
| name | Char | Ticket subject, required |
| ticket_number | Char | Auto-generated sequence (HD00001), readonly |
| description | Html | Ticket body |
| priority | Selection | Low / Medium / High / Urgent |
| stage_id | Many2one → helpdesk.stage | Current stage |
| team_id | Many2one → helpdesk.team | Assigned team |
| user_id | Many2one → res.users | Assigned agent |
| category_id | Many2one → helpdesk.category | Ticket category |
| partner_id | Many2one → res.partner | Customer (creator) |
| active | Boolean | Archive |
| stage_change_date | Datetime | Last stage transition timestamp |
| last_activity_date | Datetime | Last any activity (create/update/comment) |
| close_date | Datetime | When resolved → closed |
| create_date | Datetime | Auto-set by Odoo |

### 3.2 `helpdesk.stage`

| Field | Type | Notes |
|-------|------|-------|
| name | Char | Stage name |
| sequence | Integer | Pipeline order |
| is_start | Boolean | Default stage for new tickets |
| is_done | Boolean | Terminal stage (closed/resolved) |
| fold | Boolean | Fold in kanban (collapsed) |
| team_ids | Many2many → helpdesk.team | Restrict to teams (optional) |

### 3.3 `helpdesk.team`

| Field | Type | Notes |
|-------|------|-------|
| name | Char | Team name |
| member_ids | Many2many → res.users | Team members |
| assignment_policy | Selection | manual / round_robin / least_loaded / random |

### 3.4 `helpdesk.category`

| Field | Type | Notes |
|-------|------|-------|
| name | Char | Category name |
| team_id | Many2one → helpdesk.team | Default team |
| color | Integer | Color index for UI |
| sequence | Integer | Order in selection |
| active | Boolean | |

---

## 4. Views

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

## 5. Security

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

## 6. Engineering Principles

| Principle | Guideline |
|-----------|-----------|
| Odoo version | 19.0 Community & Enterprise |
| Python | 3.10+ |
| No N+1 queries | All list/kanban views must use `_compute` with prefetch or `search` with `_prefetch`. Avoid computed fields in tree columns that trigger per-row SQL |
| Indexing | Fields used in search/filter/group_by must have `index=True` where appropriate |
| Kanban performance | Must render smoothly with 200+ tickets per stage. No synchronous RPC on drag |
| i18n | English + Vietnamese (vi) |
| Tests | Unit tests for all models, coverage > 80% |
| CI | Manifest check, lint, test on push to main/develop |

---

## 7. Extension Points (Community → Pro)

```
helpdesk.ticket
    ├── helpdesk.ticket.sla        (Pro)  — SLA timers + escalation
    ├── helpdesk.ticket.time       (Pro)  — Timesheet integration
    ├── helpdesk.ticket.rating     (Pro)  — CSAT / NPS survey
    ├── helpdesk.ticket.ai         (Pro)  — Auto-tag, auto-assign
    └── helpdesk.kb                (Pro)  — Knowledge base / canned responses
```

Each extension uses `_inherit` on `helpdesk.ticket` — Community never needs to know Pro exists. No monkey-patching, no `if pro:` branching in Community code.

---

## 8. Acceptance Criteria

| # | Criterion | How to verify |
|---|-----------|---------------|
| 1 | Install module | Apps → Install, no errors |
| 2 | Create ticket | Fill subject + description, save. Visible in list + kanban |
| 3 | Auto-number | First ticket shows HD00001, second HD00002 |
| 4 | Assign ticket | Set team + user. State transitions New → In Progress |
| 5 | Move stage | Drag in kanban or change in form. stage_change_date updates |
| 6 | Resolve → Close | Mark Resolved → then Close. close_date set. Closed tickets read-only for non-Manager |
| 7 | Reopen | Resolved or Closed ticket → Reopen. Returns to In Progress |
| 8 | Portal create | Login as portal user → create ticket. Visible to agent |
| 9 | Portal view | Portal user sees only own tickets. Cannot see other tickets |
| 10 | Notifications | Assignee gets email on assignment. Customer gets email on state change |
| 11 | Search / Filter | Filter by team, stage, priority, assignee |
| 12 | Archive | Archive ticket → disappears from default views |
| 13 | Uninstall | Remove module → no trace left (tables dropped, no orphan records) |
| 14 | Upgrade | Upgrade from v1.0.0 → v1.1.0. No data loss. Migrations run clean |

---

## 9. Release Criteria

| Check | Required |
|-------|----------|
| All acceptance criteria pass | ✅ |
| All unit tests pass | ✅ |
| No critical lint errors | ✅ |
| README + CHANGELOG updated | ✅ |
| Screenshots in `static/description/` | ✅ |
| `__manifest__.py` complete | ✅ |
| Demo data works | ✅ |
| Portal access tested | ✅ |
| Odoo App Store listing ready | ✅ |

---

## 10. Future (Post v1.0)

- SLA timers + escalation (Pro)
- Email gateway (inbound) (Pro)
- Automated assignment policies (Pro)
- Reporting dashboard (Pro)
- Knowledge base / canned responses (Pro)
- CSAT / NPS survey (Pro)
- AI auto-tag / auto-assign (Pro)
- Multi-language translations
