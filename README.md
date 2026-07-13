# Helpdesk Community

> Support ticket management for Odoo 19.0 — Community Edition.

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

![Ticket Kanban](static/description/screenshot_kanban.png)
![Ticket Form](static/description/screenshot_form.png)
![Portal View](static/description/screenshot_portal.png)

## Installation

Install via Odoo App Store, or clone into your addons directory:

```bash
git clone https://github.com/FoxPinkHQ/helpdesk-community addons/helpdesk_community
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

- Odoo 19.0 (Community / Enterprise)

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

See [CHANGELOG.md](CHANGELOG.md).

## Support

- Issues: [GitHub Issues](https://github.com/FoxPinkHQ/helpdesk-community/issues)
- Email: aduy000@gmail.com

## License

LGPL-3 — see [LICENSE](LICENSE).
