import typer
from src.client import get_client, RELEVANT_STAGES
from src.utils import format_m2o, output_json, pick

app = typer.Typer()


@app.command()
def list(
    project_id: int = typer.Argument(None, help='Project ID'),
    json: bool = typer.Option(False, '--json', help='Output as JSON'),
):
    """List tasks, optionally filtered by project"""
    uid, models, ak, db = get_client()
    if not project_id:
        projects = models.execute_kw(db, uid, ak, 'project.project',
            'search_read', [[]], {'fields': ['id', 'name'], 'order': 'create_date DESC'})
        picked = pick(projects, prompt='Select a project')
        project_id = picked['id']
    domain = []
    if project_id:
        domain = [['project_id', '=', project_id]]
    tasks = models.execute_kw(db, uid, ak, 'project.task',
        'search_read', [domain], {
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


@app.command()
def get(
    task_id: int = typer.Argument(None, help='Task ID'),
    json: bool = typer.Option(False, '--json', help='Output as JSON'),
):
    """Show task details"""
    uid, models, ak, db = get_client()
    if not task_id:
        tasks = models.execute_kw(db, uid, ak, 'project.task',
            'search_read', [[]], {
                'fields': ['id', 'name'],
                'order': 'create_date DESC',
                'limit': 30,
            })
        picked = pick(tasks, prompt='Select a task')
        task_id = picked['id']
    task = models.execute_kw(db, uid, ak, 'project.task',
        'read', [[task_id], ['id', 'name', 'project_id', 'milestone_id', 'stage_id', 'user_ids', 'partner_id', 'x_categories', 'description', 'planned_date_start', 'date_deadline', 'create_date']])
    if not task:
        print(f'Task {task_id} not found')
        raise typer.Exit(1)
    t = task[0]
    if json:
        output_json(t)
        return
    print(f"Task [{t['id']}] {t['name']}")
    print(f"  Project   : {format_m2o(t.get('project_id'))}")
    print(f"  Milestone : {format_m2o(t.get('milestone_id'))}")
    print(f"  Stage     : {format_m2o(t.get('stage_id'))}")
    print(f"  Category  : {t.get('x_categories', '')}")
    print(f"  Assignees : {', '.join([u[1] for u in t.get('user_ids', [])]) if isinstance(t.get('user_ids'), list) else t.get('user_ids', '')}")
    print(f"  Created   : {t.get('create_date')}")


@app.command()
def create(
    project_id: int = typer.Argument(None, help='Project ID'),
    name: str = typer.Option(None, '--name', '-n', help='Task name'),
    category: str = typer.Option('Tarea tecnica', '--category', '-c', help='Category'),
    milestone_id: int = typer.Option(None, '--milestone', '-m', help='Milestone ID'),
    description: str = typer.Option('', '--description', '-d', help='Description'),
    json: bool = typer.Option(False, '--json', help='Output as JSON'),
):
    """Create a task in a project"""
    uid, models, ak, db = get_client()
    if not project_id:
        projects = models.execute_kw(db, uid, ak, 'project.project',
            'search_read', [[]], {'fields': ['id', 'name'], 'order': 'create_date DESC'})
        picked = pick(projects, prompt='Select a project')
        project_id = picked['id']
    if not milestone_id:
        milestones = models.execute_kw(db, uid, ak, 'project.milestone',
            'search_read', [[['project_id', '=', project_id]]], {
                'fields': ['id', 'name'],
                'order': 'deadline DESC, id DESC',
                'limit': 1,
            })
        milestone_id = milestones[0]['id'] if milestones else None
    task_data = {
        'name': name or f'Task - {milestones[0]["name"] if milestones else project_id}',
        'project_id': project_id,
        'milestone_id': milestone_id,
        'x_categories': category,
        'description': description,
    }
    if not milestone_id:
        del task_data['milestone_id']
    task_id = models.execute_kw(db, uid, ak, 'project.task', 'create', [task_data])
    if json:
        output_json({'id': task_id, **task_data})
        return
    print(f'Task [{task_id}] created')
    print(f'  Project   : {project_id}')
    print(f'  Milestone : {milestone_id}')
    print(f'  Category  : {category}')


@app.command()
def stage(
    task_id: int = typer.Argument(None, help='Task ID'),
    stage_id: int = typer.Argument(None, help='Stage ID'),
    json: bool = typer.Option(False, '--json', help='Output as JSON'),
):
    """Change task stage"""
    uid, models, ak, db = get_client()
    if not task_id:
        tasks = models.execute_kw(db, uid, ak, 'project.task',
            'search_read', [[]], {
                'fields': ['id', 'name'],
                'order': 'create_date DESC',
                'limit': 30,
            })
        picked = pick(tasks, prompt='Select a task')
        task_id = picked['id']
    if not stage_id:
        stages = models.execute_kw(db, uid, ak, 'project.task.type',
            'search_read', [[['id', 'in', RELEVANT_STAGES]]], {'fields': ['id', 'name'], 'order': 'id ASC'})
        picked = pick(stages, prompt='Select a stage')
        stage_id = picked['id']
    models.execute_kw(db, uid, ak, 'project.task', 'write', [[task_id], {'stage_id': stage_id}])
    stage_name = models.execute_kw(db, uid, ak, 'project.task.type', 'read', [[stage_id], ['name']])
    if json:
        output_json({'task_id': task_id, 'stage_id': stage_id, 'stage_name': stage_name[0]['name']})
        return
    print(f'Task [{task_id}] moved to stage "{stage_name[0]["name"]}"')


@app.command()
def category(
    task_id: int = typer.Argument(None, help='Task ID'),
    category: str = typer.Argument(None, help='Category name'),
    json: bool = typer.Option(False, '--json', help='Output as JSON'),
):
    """Change task category"""
    uid, models, ak, db = get_client()
    if not task_id:
        tasks = models.execute_kw(db, uid, ak, 'project.task',
            'search_read', [[]], {
                'fields': ['id', 'name'],
                'order': 'create_date DESC',
                'limit': 30,
            })
        picked = pick(tasks, prompt='Select a task')
        task_id = picked['id']
    if not category:
        category = 'Tarea tecnica'
    models.execute_kw(db, uid, ak, 'project.task', 'write', [[task_id], {'x_categories': category}])
    if json:
        output_json({'task_id': task_id, 'category': category})
        return
    print(f'Task [{task_id}] category set to "{category}"')
