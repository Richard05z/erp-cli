# Milestone (sprint/hito) commands
import typer
from src.client import get_client
from src.utils import format_m2o, output_json, pick

app = typer.Typer(no_args_is_help=True)


@app.command()
def list(
    project_id: int = typer.Argument(None, help='Filter by project ID'),
    json: bool = typer.Option(False, '--json', help='Output as JSON'),
):
    """List milestones (optionally filtered by project)"""
    uid, models, ak, db = get_client()
    domain = []
    if project_id:
        domain = [['project_id', '=', project_id]]
    milestones = models.execute_kw(db, uid, ak, 'project.milestone',
        'search_read', [domain], {
            'fields': ['id', 'name', 'deadline', 'start_date', 'project_id', 'is_reached', 'task_count', 'done_task_count'],
            'order': 'deadline DESC',
        })
    if json:
        output_json(milestones)
        return
    print(f'Milestones ({len(milestones)}):\n')
    for m in milestones:
        proj = format_m2o(m.get('project_id'))
        reached = 'Yes' if m.get('is_reached') else 'No'
        print(f"  [{m['id']}] {m['name']}  |  {proj}")
        print(f"         {m.get('start_date')} -> {m.get('deadline')}  |  reached={reached}  |  tasks={m.get('done_task_count')}/{m.get('task_count')}")
        print()
