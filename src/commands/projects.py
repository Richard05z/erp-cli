import typer
from src.client import get_client
from src.utils import format_m2o, output_json, pick, paginated_display

app = typer.Typer(no_args_is_help=True)


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
    all_tasks: bool = typer.Option(False, '--all', '-a', help='Show all tasks without pagination'),
    limit: int = typer.Option(30, '--limit', '-l', help='Items per page'),
    json: bool = typer.Option(False, '--json', help='Output as JSON'),
):
    """List tasks of a project"""
    uid, models, ak, db = get_client()
    if not project_id:
        projects = models.execute_kw(db, uid, ak, 'project.project',
            'search_read', [[]], {'fields': ['id', 'name'], 'order': 'create_date DESC'})
        picked = pick(projects, prompt='Select a project')
        project_id = picked['id']

    proj = models.execute_kw(db, uid, ak, 'project.project', 'read', [[project_id], ['name']])
    proj_name = proj[0]['name'] if proj else project_id

    if json:
        tasks = models.execute_kw(db, uid, ak, 'project.task',
            'search_read', [[['project_id', '=', project_id]]], {
                'fields': ['id', 'name', 'user_ids', 'stage_id', 'x_categories', 'milestone_id', 'create_date'],
                'order': 'create_date DESC',
            })
        output_json(tasks)
        return

    if all_tasks:
        tasks = models.execute_kw(db, uid, ak, 'project.task',
            'search_read', [[['project_id', '=', project_id]]], {
                'fields': ['id', 'name', 'user_ids', 'stage_id', 'x_categories', 'milestone_id', 'create_date'],
                'order': 'create_date DESC',
            })
        print(f'Total: {len(tasks)}\n')
        for t in tasks:
            stage = format_m2o(t.get('stage_id'))
            cat = t.get('x_categories', '')
            milestone = format_m2o(t.get('milestone_id'))
            print(f"  [{t['id']}] {t['name']}")
            print(f"         stage={stage}  category={cat}  milestone={milestone}")
            print()
        return

    total = models.execute_kw(db, uid, ak, 'project.task', 'search_count', [[['project_id', '=', project_id]]])
    print(f'Tasks for {proj_name} ({total} total):\n')

    def fetch_page(offset, page_limit):
        return models.execute_kw(db, uid, ak, 'project.task',
            'search_read', [[['project_id', '=', project_id]]], {
                'fields': ['id', 'name', 'user_ids', 'stage_id', 'x_categories', 'milestone_id', 'create_date'],
                'order': 'create_date DESC',
                'offset': offset,
                'limit': page_limit,
            })

    def display(items, offset):
        for t in items:
            stage = format_m2o(t.get('stage_id'))
            cat = t.get('x_categories', '')
            milestone = format_m2o(t.get('milestone_id'))
            print(f"  [{t['id']}] {t['name']}")
            print(f"         stage={stage}  category={cat}  milestone={milestone}")
            print()

    paginated_display(fetch_page, display, page_size=limit)
