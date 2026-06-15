# ERP CLI

CLI tool for Odoo ERP project management via XML-RPC.

## Quick start

```bash
pip install .
cp .env.example .env          # then fill in your credentials
python3 erp-cli.py --help
```

### Requirements

- Python >= 3.8
- An Odoo instance with XML-RPC enabled

## Environment

| Variable | Description |
|----------|-------------|
| `ERP_URL` | Odoo instance URL (e.g. `https://your-odoo.com`) |
| `ERP_DB` | Database name |
| `ERP_LOGIN` | User email |
| `ERP_API_KEY` | API key |

All four are required.

## Usage

```
python3 erp-cli.py project list                 List all projects
python3 erp-cli.py task list                    List tasks (interactive pickers)
python3 erp-cli.py task get <id>                Show task details
python3 erp-cli.py task create                  Create a task interactively
python3 erp-cli.py task stage <id> <stage>      Change task stage
python3 erp-cli.py milestone list               List milestones
python3 erp-cli.py stage list                   List stages
python3 erp-cli.py user list                    List users
```

Use `./dist/erp-cli` instead of `python3 erp-cli.py` if using the compiled binary.

All commands accept `--json` for JSON output and `--help` for details.

## Standalone binary

After compiling, a standalone binary is generated at `dist/erp-cli` (no Python required):

```bash
pip install pyinstaller
pyinstaller erp-cli.spec
./dist/erp-cli project list
```

## Project structure

```
├── erp-cli.py          # Entry point
├── src/
│   ├── client.py       # Odoo XML-RPC connection
│   ├── main.py         # Typer app
│   ├── utils.py        # Shared utilities
│   └── commands/       # Command modules
├── .env                # Local config (gitignored)
├── .env.example        # Config template
├── pyproject.toml
└── erp-cli.spec        # PyInstaller spec
```

## License

MIT
