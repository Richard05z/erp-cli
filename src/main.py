# Typer app entry point — registers all subcommand groups
import typer
from .commands import projects, milestones, tasks, stages, users

app = typer.Typer(
    name='erp-cli',
    help='CLI tool for ERP Odoo project management',
    no_args_is_help=True,
    add_completion=True,
)

app.add_typer(projects.app, name='project', help='Manage projects')
app.add_typer(milestones.app, name='milestone', help='Manage milestones')
app.add_typer(tasks.app, name='task', help='Manage tasks')
app.add_typer(stages.app, name='stage', help='Manage stages')
app.add_typer(users.app, name='user', help='Manage users')
