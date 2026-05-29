import typer
from src.client import get_client, RELEVANT_STAGES
from src.utils import output_json

app = typer.Typer()


@app.command()
def list(
    all: bool = typer.Option(False, '--all', help='Show all stages, not just the 5 main ones'),
    json: bool = typer.Option(False, '--json', help='Output as JSON'),
):
    """List task stages (only New, In process, Despliegue, Test, Finish by default)"""
    uid, models, ak, db = get_client()
    domain = [['id', 'in', RELEVANT_STAGES]] if not all else []
    stages = models.execute_kw(db, uid, ak, 'project.task.type',
        'search_read', [domain], {'fields': ['id', 'name'], 'order': 'id ASC'})
    if json:
        output_json(stages)
        return
    print(f'Stages ({len(stages)}):\n')
    for s in stages:
        print(f"  [{s['id']}] {s['name']}")
