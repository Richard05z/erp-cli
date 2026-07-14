# Task CRUD and lifecycle commands: list, get, create, change stage/category
import typer
from src.client import get_client, RELEVANT_STAGES
from src.utils import format_m2o, output_json, pick, paginated_pick, paginated_display


app = typer.Typer(no_args_is_help=True)


@app.command()
def list(
    project_id: int = typer.Argument(None, help="Project ID"),
    milestone_id: int = typer.Option(None, "--milestone", "-m", help="Milestone ID"),
    stage_id: int = typer.Option(None, "--stage", "-s", help="Stage ID"),
    all_tasks: bool = typer.Option(
        False, "--all", "-a", help="Show all tasks without pagination"
    ),
    limit: int = typer.Option(30, "--limit", "-l", help="Items per page"),
    json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """List tasks, optionally filtered by project, milestone, and stage"""
    uid, models, ak, db = get_client()
    # Pick project interactively if not provided
    if not project_id:
        projects = models.execute_kw(
            db,
            uid,
            ak,
            "project.project",
            "search_read",
            [[]],
            {"fields": ["id", "name"], "order": "create_date DESC"},
        )
        picked = pick(projects, prompt="Select a project")
        project_id = picked["id"]
        # If applicable, also pick a milestone for the selected project
        milestones = models.execute_kw(
            db,
            uid,
            ak,
            "project.milestone",
            "search_read",
            [[["project_id", "=", project_id]]],
            {
                "fields": ["id", "name", "deadline"],
                "order": "deadline DESC",
            },
        )
        if milestones:
            milestones.insert(0, {"id": None, "name": "(All milestones)"})
            picked = pick(milestones, prompt="Select a milestone (optional)")
            milestone_id = picked.get("id")
        # Interactive stage selection (optional)
        stages = models.execute_kw(
            db,
            uid,
            ak,
            "project.task.type",
            "search_read",
            [[["id", "in", RELEVANT_STAGES]]],
            {"fields": ["id", "name"], "order": "id ASC"},
        )
        if stages:
            stages.insert(0, {"id": None, "name": "(All stages)"})
            picked = pick(stages, prompt="Select a stage (optional)")
            stage_id = picked.get("id")
    domain = [["project_id", "=", project_id]]
    if milestone_id:
        domain.append(["milestone_id", "=", milestone_id])
    if stage_id:
        domain.append(["stage_id", "=", stage_id])

    proj = models.execute_kw(
        db, uid, ak, "project.project", "read", [[project_id], ["name"]]
    )
    proj_name = proj[0]["name"] if proj else project_id

    if json:
        tasks = models.execute_kw(
            db,
            uid,
            ak,
            "project.task",
            "search_read",
            [domain],
            {
                "fields": [
                    "id",
                    "name",
                    "user_ids",
                    "stage_id",
                    "x_categories",
                    "milestone_id",
                    "create_date",
                ],
                "order": "create_date DESC",
            },
        )
        output_json(tasks)
        return

    if all_tasks:
        tasks = models.execute_kw(
            db,
            uid,
            ak,
            "project.task",
            "search_read",
            [domain],
            {
                "fields": [
                    "id",
                    "name",
                    "user_ids",
                    "stage_id",
                    "x_categories",
                    "milestone_id",
                    "create_date",
                ],
                "order": "create_date DESC",
            },
        )
        print(f"Total: {len(tasks)}\n")
        for t in tasks:
            stage = format_m2o(t.get("stage_id"))
            cat = t.get("x_categories", "")
            milestone = format_m2o(t.get("milestone_id"))
            print(f"  [{t['id']}] {t['name']}")
            print(f"         stage={stage}  category={cat}  milestone={milestone}")
            print()
        return

    total = models.execute_kw(db, uid, ak, "project.task", "search_count", [domain])
    print(f"Tasks for {proj_name} ({total} total):\n")

    def fetch_page(offset, page_limit):
        return models.execute_kw(
            db,
            uid,
            ak,
            "project.task",
            "search_read",
            [domain],
            {
                "fields": [
                    "id",
                    "name",
                    "user_ids",
                    "stage_id",
                    "x_categories",
                    "milestone_id",
                    "create_date",
                ],
                "order": "create_date DESC",
                "offset": offset,
                "limit": page_limit,
            },
        )

    def display(items, offset):
        for t in items:
            stage = format_m2o(t.get("stage_id"))
            cat = t.get("x_categories", "")
            milestone = format_m2o(t.get("milestone_id"))
            print(f"  [{t['id']}] {t['name']}")
            print(f"         stage={stage}  category={cat}  milestone={milestone}")
            print()

    paginated_display(fetch_page, display, page_size=limit)


@app.command()
def get(
    task_id: int = typer.Argument(None, help="Task ID"),
    json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show task details"""
    uid, models, ak, db = get_client()
    # Pick task interactively with paginated picker if not provided
    if not task_id:

        def fetch_page(offset, limit):
            return models.execute_kw(
                db,
                uid,
                ak,
                "project.task",
                "search_read",
                [[]],
                {
                    "fields": ["id", "name"],
                    "order": "create_date DESC",
                    "offset": offset,
                    "limit": limit,
                },
            )

        picked = paginated_pick(fetch_page, prompt="Select a task")
        task_id = picked["id"]
    task = models.execute_kw(
        db,
        uid,
        ak,
        "project.task",
        "read",
        [
            [task_id],
            [
                "id",
                "name",
                "project_id",
                "milestone_id",
                "stage_id",
                "user_ids",
                "partner_id",
                "x_categories",
                "description",
                "date_deadline",
                "create_date",
            ],
        ],
    )
    if not task:
        print(f"Task {task_id} not found")
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
    user_ids = t.get("user_ids")
    assignees = str(user_ids or "")
    print(f"  Assignees : {assignees}")
    print(f"  Created   : {t.get('create_date')}")


@app.command()
def create(
    json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Create a task interactively"""
    uid, models, ak, db = get_client()

    projects = models.execute_kw(
        db,
        uid,
        ak,
        "project.project",
        "search_read",
        [[]],
        {"fields": ["id", "name"], "order": "create_date DESC"},
    )
    picked = pick(projects, prompt="Select a project")
    project_id = picked["id"]

    name = input("Task name: ").strip()
    while not name:
        name = input("Task name (required): ").strip()

    milestones = models.execute_kw(
        db,
        uid,
        ak,
        "project.milestone",
        "search_read",
        [[["project_id", "=", project_id]]],
        {
            "fields": ["id", "name", "deadline"],
            "order": "deadline DESC",
        },
    )
    milestone_id = None
    if milestones:
        milestones.insert(0, {"id": None, "name": "(No milestone)"})
        picked = pick(milestones, prompt="Select a milestone")
        milestone_id = picked.get("id")

    cat = pick(
        [
            {"id": "Tarea tecnica", "name": "Tarea tecnica"},
            {"id": "Historia de usuario", "name": "Historia de usuario"},
            {"id": "Caso de Prueba", "name": "Caso de Prueba"},
        ],
        prompt="Select a category",
    )["id"]
    category = cat

    description = input("Description (optional): ").strip()

    task_data = {
        "name": name,
        "project_id": project_id,
        "x_categories": category,
    }
    if milestone_id:
        task_data["milestone_id"] = milestone_id
    if description:
        task_data["description"] = description

    task_id = models.execute_kw(db, uid, ak, "project.task", "create", [task_data])
    if json:
        output_json({"id": task_id, **task_data})
        return
    print(f"Task [{task_id}] created")
    print(f"  Project   : {project_id}")
    print(f"  Milestone : {milestone_id}")
    print(f"  Category  : {category}")


@app.command()
def stage(
    task_id: int = typer.Argument(None, help="Task ID"),
    stage_id: int = typer.Argument(None, help="Stage ID"),
    json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Change task stage"""
    uid, models, ak, db = get_client()
    if not task_id:

        def fetch_page(offset, limit):
            return models.execute_kw(
                db,
                uid,
                ak,
                "project.task",
                "search_read",
                [[]],
                {
                    "fields": ["id", "name"],
                    "order": "create_date DESC",
                    "offset": offset,
                    "limit": limit,
                },
            )

        picked = paginated_pick(fetch_page, prompt="Select a task")
        task_id = picked["id"]
    if not stage_id:
        stages = models.execute_kw(
            db,
            uid,
            ak,
            "project.task.type",
            "search_read",
            [[["id", "in", RELEVANT_STAGES]]],
            {"fields": ["id", "name"], "order": "id ASC"},
        )
        picked = pick(stages, prompt="Select a stage")
        stage_id = picked["id"]
    models.execute_kw(
        db, uid, ak, "project.task", "write", [[task_id], {"stage_id": stage_id}]
    )
    stage_name = models.execute_kw(
        db, uid, ak, "project.task.type", "read", [[stage_id], ["name"]]
    )
    if json:
        output_json(
            {
                "task_id": task_id,
                "stage_id": stage_id,
                "stage_name": stage_name[0]["name"],
            }
        )
        return
    print(f'Task [{task_id}] moved to stage "{stage_name[0]["name"]}"')


@app.command()
def category(
    task_id: int = typer.Argument(None, help="Task ID"),
    category: str = typer.Argument(None, help="Category name"),
    json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Change task category"""
    uid, models, ak, db = get_client()
    if not task_id:

        def fetch_page(offset, limit):
            return models.execute_kw(
                db,
                uid,
                ak,
                "project.task",
                "search_read",
                [[]],
                {
                    "fields": ["id", "name"],
                    "order": "create_date DESC",
                    "offset": offset,
                    "limit": limit,
                },
            )

        picked = paginated_pick(fetch_page, prompt="Select a task")
        task_id = picked["id"]
    if not category:
        category = "Tarea tecnica"
    models.execute_kw(
        db, uid, ak, "project.task", "write", [[task_id], {"x_categories": category}]
    )
    if json:
        output_json({"task_id": task_id, "category": category})
        return
    print(f'Task [{task_id}] category set to "{category}"')
