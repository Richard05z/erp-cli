# Stage (project.task.type) commands
import typer
from src.client import get_client, RELEVANT_STAGES
from src.utils import output_json

app = typer.Typer(no_args_is_help=True)


@app.command()
def list(
    all: bool = typer.Option(False, '--all', help='Show all stages, not just the 5 main ones'),
    json: bool = typer.Option(False, '--json', help='Output as JSON'),
):
    """List task stages (only New, In process, Despliegue, Test, Finish by default)"""
    uid, models, ak, db = get_client()
    # Without --all, only show the 5 stages relevant for task stage changes
    domain = [['id', 'in', RELEVANT_STAGES]] if not all else []
    stages = models.execute_kw(db, uid, ak, 'project.task.type',
        'search_read', [domain], {'fields': ['id', 'name'], 'order': 'id ASC'})
    if json:
        output_json(stages)
        return
    print(f'Stages ({len(stages)}):\n')
    for s in stages:
        print(f"  [{s['id']}] {s['name']}")
