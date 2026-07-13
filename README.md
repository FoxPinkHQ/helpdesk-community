# Helpdesk Community

> Support ticket management for **Odoo 17.0** — Community Edition.

**Version:** 17.0.1.0.4 · **License:** LGPL-3 · **Publisher:** FoxPink · Maintained for **Odoo 14.0 – 19.0** (one validated build per series)

## Features

- Tickets with customizable pipeline (New → In Progress → Resolved → Closed)
- Teams with agents and assignment policies
- Categories for ticket classification
- Customer portal — users can create and track tickets
- Email notifications on assignment and stage changes
- Kanban view for drag-and-drop pipeline management
- Full search and filter by stage, team, priority, assignee
- Three-tier access control (User / Team Leader / Manager)

## Screenshots

![Ticket Kanban](helpdesk_community/static/description/screenshot_01_kanban.png)
![Ticket Form](helpdesk_community/static/description/screenshot_02_form.png)
![Ticket List](helpdesk_community/static/description/screenshot_03_list.png)
![Portal — My Tickets](helpdesk_community/static/description/screenshot_06_portal_list.png)
![Portal — Ticket Detail](helpdesk_community/static/description/screenshot_07_portal_detail.png)

## Installation

Install via the Odoo Apps Store, or download the ZIP for **your Odoo version** from
[Releases](https://github.com/FoxPinkHQ/helpdesk-community/releases) and unzip it
into your addons directory. To track this series from git:

```bash
git clone -b 17.0 https://github.com/FoxPinkHQ/helpdesk-community addons/helpdesk_community
```

Restart Odoo, activate Developer Mode, then go to Apps → Update Apps List. Search for "Helpdesk Community" and install.

## Configuration

1. Go to Helpdesk → Configuration → Stages to customize your pipeline
2. Go to Helpdesk → Configuration → Teams to create teams and add members
3. Go to Helpdesk → Configuration → Categories to classify tickets
4. Default pipeline: New → In Progress → Resolved → Closed

## Dependencies

- `base` (always)
- `mail` (email notifications)
- `portal` (customer access)
- `web` (kanban views)

## Compatibility

- **This build:** Odoo 17.0 (Community / Enterprise)
- Maintained across **Odoo 14.0, 15.0, 16.0, 17.0, 18.0, 19.0** — install the build matching your Odoo version. Each series has its own git branch and its own validated release ZIP.
- **Quality gates (see [ADR-003](docs/adr/003-three-tier-quality-gates.md)):** Build + Render smoke pass on all series 14.0–19.0; full behavior UAT (real user actions + overflow) runs on the canonical 19.0.

## Community vs Pro

| Feature | Community | Pro |
|---------|-----------|-----|
| Ticket management | ✅ | ✅ |
| Stages / Pipeline | ✅ | ✅ |
| Teams & Assignees | ✅ | ✅ |
| Customer Portal | ✅ | ✅ |
| Email notifications | ✅ | ✅ |
| SLA management | ❌ | ✅ |
| Email gateway | ❌ | ✅ |
| Automated actions | ❌ | ✅ |
| Advanced reporting | ❌ | ✅ |
| Time tracking | ❌ | ✅ |

## Changelog

See [docs/CHANGELOG.md](docs/CHANGELOG.md). Latest: **17.0.1.0.4** — fixed Bugs A–E (category color save, portal CSRF, stage default, assign, filter labels) and mail-template rendering.

## Support

- Issues: [GitHub Issues](https://github.com/FoxPinkHQ/helpdesk-community/issues)
- Email: aduy000@gmail.com

## License

LGPL-3 — see [LICENSE](LICENSE).
