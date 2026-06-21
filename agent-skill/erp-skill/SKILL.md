---
name: erp-cli
description: Odoo ERP CLI tool for project management. Commands: project, task, milestone, stage, user. All support --json. Uses questionary interactive selectors.
---

# ERP CLI — Agent Instructions

You MUST use this CLI tool for ALL interactions with the ERP system. Do NOT access the Odoo database, API, or web interface directly. Do NOT write scripts that call the Odoo XML-RPC API bypassing the CLI.

If the user asks for something that the CLI cannot do (e.g. create a project, delete a task, modify a user), respond clearly: **"That operation is not supported by the CLI."** Do not attempt to implement it by other means.

Follow these steps:

1. Identify which CLI command matches the user's request using the tables below.
2. Run the command and return the result to the user.
3. If no command exists for the requested operation, inform the user it's not supported.

CLI tool for Odoo ERP project management via XML-RPC API.

## Project Location

```
/var/www/erp-cli/
├── erp-cli.py          # Entry point (python3 erp-cli.py <command>)
├── dist/erp-cli        # Pre-compiled binary (ELF x86-64, standalone)
├── src/                # Python source package
│   ├── client.py       # Odoo XML-RPC connection (URL, DB, auth)
│   ├── main.py         # Typer app definition and command registration
│   ├── utils.py        # pick(), paginated_pick(), paginated_display(), format_m2o(), output_json()
│   └── commands/       # Subcommand modules
│       ├── projects.py
│       ├── tasks.py
│       ├── milestones.py
│       ├── stages.py
│       └── users.py
├── .env                # Required: ERP_URL, ERP_DB, ERP_LOGIN, ERP_API_KEY
├── .env.example        # Template for .env (safe to commit)
├── pyproject.toml      # Python project config
└── erp-cli.spec        # PyInstaller spec for binary build
```

## Setup & Execution

### Prerequisites
- Python >= 3.8
- Dependencies: `typer`, `python-dotenv`, `questionary`

### Setup
```bash
pip install .
cp .env.example .env   # then fill in your credentials
```

### Running
```bash
# Via source (development)
python3 erp-cli.py <command> [subcommand] [options]

# Via installed package
pip install .
erp-cli <command> [subcommand] [options]

# Via standalone binary (no Python needed)
./dist/erp-cli <command> [subcommand] [options]

# Build binary
pyinstaller erp-cli.spec
```

### Configuration (`.env`) — copy from `.env.example`:
```bash
cp .env.example .env
```

All four variables are **required**. The CLI will exit immediately if any is missing.

Example `.env`:
```
ERP_URL=https://your-odoo-instance.com
ERP_DB=your-database-name
ERP_LOGIN=your-email@example.com
ERP_API_KEY=your-api-key
```

XML-RPC endpoints:
- `/xmlrpc/2/common` — authenticate, version check
- `/xmlrpc/2/object` — model CRUD operations

Auth flow: `common.authenticate(DB, LOGIN, API_KEY, {})` → returns `uid`.
All subsequent calls use `models.execute_kw(db, uid, ak, model, method, args, kwargs)`.

## Business Logic & Workflows

### Project Lifecycle
1. Projects are created in Odoo manually (no CLI command to create)
2. Tasks are created within projects via `task create`
3. Tasks move through stages: New → In process → Despliegue → Test → Finish
4. Each task has a category: Tarea tecnica, Historia de usuario, or Caso de Prueba
5. Tasks can be assigned to milestones (sprints/hitos) within a project

### Task Creation Flow (interactive)
When `task create` is run:
1. **Select project** — picker shows all projects ordered by creation date
2. **Enter name** — required, cannot be empty
3. **Select milestone** — shows milestones for the chosen project; option to skip (No milestone)
4. **Select category** — predefined options: Tarea tecnica (default), Historia de usuario, Caso de Prueba
5. **Enter description** — optional, free text

### Task Stage Change Flow
When `task stage` is run:
1. If no task ID: picker shows tasks with pagination (30 per page, "(Show more...)" option)
2. If no stage ID: picker shows the 5 relevant stages
3. Stage is updated via `project.task.write()` on the server
4. Confirmation message shows the new stage name

### Task Category Change Flow
When `task category` is run:
1. If no task ID: picker shows tasks with pagination (30 per page, "(Show more...)" option)
2. If no category: defaults to "Tarea tecnica"
3. Category is updated via `project.task.write()` on the server

## Available Commands

All commands auto-show `--help` when invoked without arguments.

### `project`

| Subcommand | Args | Flags | Description |
|------------|------|-------|-------------|
| `list` | — | `--json` | List all projects with ID, name, user, stage |
| `tasks` | `[PROJECT_ID]` | `--all, -a`, `--limit, -l`, `--json` | List tasks of a project (pickers if omitted). `--all` disables pagination, `--limit` sets page size (default 30) |

### `task`

| Subcommand | Args | Flags | Description |
|------------|------|-------|-------------|
| `list` | `[PROJECT_ID]` | `--milestone, -m`, `--all, -a`, `--limit, -l`, `--json` | Lists tasks, picks project then milestone if omitted. `--all` disables pagination, `--limit` sets page size (default 30) |
| `get` | `[TASK_ID]` | `--json` | Full task details: project, milestone, stage, category, assignees, dates, description |
| `create` | — | `--json` | Fully interactive: project → name → milestone → category → description |
| `stage` | `[TASK_ID]` `[STAGE_ID]` | `--json` | Change task stage (pickers if omitted) |
| `category` | `[TASK_ID]` `[CATEGORY]` | `--json` | Change task category (picker if omitted) |

### `milestone`

| Subcommand | Args | Flags | Description |
|------------|------|-------|-------------|
| `list` | `[PROJECT_ID]` | `--json` | Milestones with deadline, start date, reached status, task counts |

### `stage`

| Subcommand | Args | Flags | Description |
|------------|------|-------|-------------|
| `list` | — | `--all`, `--json` | Shows stages. Without `--all`, only 5 main stages |

### `user`

| Subcommand | Args | Flags | Description |
|------------|------|-------|-------------|
| `list` | — | `--json` | Users with name, login, email |

## Constraints & Important Notes

- **CLI-only**: Do not access Odoo directly via API, database, or web interface. Use only the commands documented here.
- **Unsupported operations**: If a user requests something not listed below, tell them it's not supported. Do not implement workarounds.
- **No delete/update commands exist** for projects, milestones, or users. Only task stage and task category can be modified.
- **Task search is limited**: `search_read` with domain filters. No full-text search.
- **Pagination**: List commands default to 30 items per page with a "Show more?" prompt. Use `--limit` to change page size or `--all` to disable pagination.
- **Paginated pickers**: Task pickers in `get`, `stage`, `category` include a "(Show more...)" option to browse beyond the first 30 tasks.
- **`planned_date_start` field removed**: The Odoo instance doesn't have this field on `project.task`.
- **`user_ids` format**: Odoo XML-RPC returns `[id]` (list of ints), not `[id, name]` pairs in `read()`.
- **Binary in `dist/`**: Pre-compiled with PyInstaller. No Python needed to run it.
- **Internet required**: Connects to the Odoo instance configured via `ERP_URL` — no offline mode.
- **Only internal users**: `user list` filters with `[['share', '=', False]]` (excludes portal/public users).
- **`api-key` file deprecated**: The old `api-key` file at project root still works as fallback but `.env` is preferred.

## Interactive Selector Behavior

All pickers (`pick()` in `utils.py`) use `questionary.select()` with:
- `use_search_filter=True` — type to filter options
- `use_jk_keys=False` — disabled to avoid conflict with search typing
- Navigation with arrow keys, confirm with Enter
- Cancel with Ctrl+C

The `pick()` function accepts items (dicts) and uses `name` field by default for display labels. Extra fields like `deadline`, `date_start`, or `create_date` are shown alongside the label.

### Paginated Pickers (`paginated_pick()`)
When there are many items (e.g., task pickers in `get`, `stage`, `category`), a special picker is used:
- Shows 30 items at a time
- If more items exist, a `(Show more...)` option appears at the bottom
- Selecting it loads the next page
- This repeats until the user picks an item or cancels

### Paginated Display (`paginated_display()`)
For list commands that may return many results:
- Shows a page of items (default 30, configurable via `--limit`)
- Prompts `"Show more?"` after each page
- Continues until no more items or user declines
- Use `--all` to skip pagination entirely
