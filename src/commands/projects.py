import typer
from src.client import get_client
from src.utils import format_m2o, output_json, pick

app = typer.Typer()


@app.command()
def list(
    json: bool = typer.Option(False, '--json', help='Output as JSON'),
):
    """List all projects"""
    uid, models, ak, db = get_client()
    projects = models.execute_kw(db, uid, ak, 'project.project',
        'search_read', [[]], {
            'fields': ['id', 'name', 'user_id', 'partner_id', 'date_start', 'date', 'stage_id'],
            'order': 'create_date DESC',
        })
    if json:
        output_json(projects)
        return
    print(f'Projects ({len(projects)}):\n')
    for p in projects:
        user = format_m2o(p.get('user_id'))
        stage = format_m2o(p.get('stage_id'))
        print(f"  [{p['id']}] {p['name']}  |  {user}  |  {stage}")


@app.command()
def tasks(
    project_id: int = typer.Argument(None, help='Project ID'),
    json: bool = typer.Option(False, '--json', help='Output as JSON'),
):
    """List tasks of a project"""
    uid, models, ak, db = get_client()
    if not project_id:
        projects = models.execute_kw(db, uid, ak, 'project.project',
            'search_read', [[]], {'fields': ['id', 'name'], 'order': 'create_date DESC'})
        picked = pick(projects, prompt='Select a project')
        project_id = picked['id']
    tasks = models.execute_kw(db, uid, ak, 'project.task',
        'search_read', [[['project_id', '=', project_id]]], {
            'fields': ['id', 'name', 'user_ids', 'stage_id', 'x_categories', 'milestone_id', 'create_date'],
            'order': 'create_date DESC',
        })
    if json:
        output_json(tasks)
        return
    proj = models.execute_kw(db, uid, ak, 'project.project', 'read', [[project_id], ['name']])
    proj_name = proj[0]['name'] if proj else project_id
    print(f'Tasks for {proj_name} ({len(tasks)}):\n')
    for t in tasks:
        stage = format_m2o(t.get('stage_id'))
        cat = t.get('x_categories', '')
        milestone = format_m2o(t.get('milestone_id'))
        print(f"  [{t['id']}] {t['name']}")
        print(f"         stage={stage}  category={cat}  milestone={milestone}")
        print()
