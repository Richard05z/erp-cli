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

## Business Logic

### Project Lifecycle
1. Projects are created in Odoo manually (no CLI command to create)
2. Tasks are created within projects via `task create`
3. Tasks move through stages: New → In process → Despliegue → Test → Finish
4. Tasks can be assigned to milestones (sprints/hitos) within a project

### Task Hierarchy
All elements of the development flow are managed as tasks, differentiated by category:
- **HU** (Historia de Usuario) → Tarea padre
- **Tarea Técnica** (TT) → Subtarea de una HU
- **Caso de Prueba** (CP) → Subtarea de una TT

This hierarchy is enforced via the Odoo parent/subtask relationship (`parent_id`).

### Task Creation Flow (interactive)
When `task create` is run:
1. **Select project** — picker shows all projects ordered by creation date
2. **Enter name** — required, cannot be empty
3. **Select milestone** — shows milestones for the chosen project; option to skip
4. **Select category** — Tarea tecnica (default), Historia de usuario, Caso de Prueba
5. **Enter description** — optional, free text

### Task Edit Flow (interactive)
When `task edit` is run without flags:
1. If no TASK_ID: pick project first, then paginated picker to select a task within that project
2. Shows current task data and prompts each field:
   - **Name** — input with current value as default
   - **Description** — optional input with current value as default
   - **Milestone** — picker of project milestones with "(No milestone)" option
   - **Assignees** — comma-separated user IDs (list all users to find IDs)
   - **Stage** — picker of the 5 main stages with "(Keep current)" option
   - **Category** — picker: HU, Tarea tecnica, Caso de Prueba with "(Keep current)" option
3. All changes are applied together via `write()`
4. If no changes made, shows "No changes made"

## Available Commands

All commands auto-show `--help` when invoked without arguments.

### `project`

| Subcommand | Args | Flags | Description |
|------------|------|-------|-------------|
| `list` | — | `--json` | List all projects with ID, name, user, stage |
| `tasks` | `[PROJECT_ID]` | `--all, -a`, `--limit, -l`, `--json` | List tasks of a project (pickers if omitted) |

### `task`

| Subcommand | Args | Flags | Description |
|------------|------|-------|-------------|
| `list` | `[PROJECT_ID]` | `--milestone, -m`, `--stage, -s`, `--all, -a`, `--limit, -l`, `--json` | Lists tasks, picks project/milestone/stage if omitted |
| `get` | `[TASK_ID]` | `--json` | Full task details: project, milestone, stage, category, assignees, dates, description |
| `create` | — | `--json` | Fully interactive: project → name → milestone → category → description |
| `edit` | `[TASK_ID]` | `--name, -n`, `--description, -d`, `--milestone, -m`, `--assignees, -a`, `--stage, -s`, `--category, -c`, `--json` | Edit a task (interactive if no flags). Milestone `0` removes it. Assignees: comma-separated IDs |
| `delete` | `[TASK_ID]` | `--force, -f`, `--json` | Delete a task (asks confirmation unless `--force`). Interactive picker if no ID |
| `board` | `[PROJECT_ID]` | `--milestone, -m`, `--json` | Kanban-style board grouped by stage |

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

## Constraints

- **CLI-only**: Do not access Odoo directly via API, database, or web interface. Use only the commands documented here.
- **No delete/update commands exist** for projects, milestones, or users. Only tasks can be modified (`task edit`) or deleted (`task delete`).
- **Pagination**: List commands default to 30 items per page. Use `--limit` to change page size or `--all` to disable pagination. Task pickers in `get`, `edit` include a "(Show more...)" option.
- **Only internal users**: `user list` excludes portal/public users.
- **Interactive pickers**: All selectors support search filtering (type to filter) and navigation with arrow keys. Cancel with Ctrl+C.
