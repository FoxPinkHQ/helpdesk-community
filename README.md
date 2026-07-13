# Odoo Module Template

> GitHub template for creating new Odoo modules with FoxPink engineering standards.

## Usage

1. Click **"Use this template"** → **"Create a new repository"**
2. Name your repo `{module_name}`
3. Clone your new repo
4. Rename `addon/` to your module's technical name
5. Edit `__manifest__.py` and implement your models/views
6. Update `README.md`, `CHANGELOG.md`, and screenshots

## Structure

```
├── addon/                  # Odoo module (rename to match your module)
│   ├── __init__.py
│   ├── __manifest__.py
│   ├── models/             # Python models
│   ├── views/              # XML views
│   ├── security/           # Access control
│   ├── demo/               # Demo data
│   ├── data/               # Default data
│   ├── wizards/            # Wizard models/views
│   ├── tests/              # Unit tests
│   └── static/description/ # Screenshots, icon, banner
├── docs/                   # Module documentation
│   ├── CHANGELOG.md
│   ├── SUPPORT.md
│   └── FAQ.md
├── screenshots/            # App store screenshots
├── .github/workflows/      # CI configuration
└── README.md
```

## Odoo 19 Notes

- Use `<list>` instead of `<tree>` in views
- Use `<card>` instead of `<kanban-box>` in kanban views
- Use `group_ids` instead of `groups_id` for res.groups
- See `docs/` for full compatibility notes

## License

LGPL-3 — see [LICENSE](LICENSE).
