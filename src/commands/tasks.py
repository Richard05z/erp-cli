# Task CRUD and lifecycle commands: list, get, create, change stage/category
import typer
from src.client import get_client, RELEVANT_STAGES
from src.utils import output_json, pick, paginated_pick, paginated_display
from questionary import confirm
from src.ui import console, print_task_table, print_task_detail, print_success


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
        print_task_table(tasks, title=f"Tasks for {proj_name} (all {len(tasks)})")
        return

    total = models.execute_kw(db, uid, ak, "project.task", "search_count", [domain])
    console.print(f"\n[bold]Tasks for {proj_name}[/] ({total} total)\n")

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
        print_task_table(items)

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
    print_task_detail(t)


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
    print_success(f"Task [{task_id}] created")
    console.print(f"  Project   : {project_id}")
    console.print(f"  Milestone : {milestone_id or '-'}")
    console.print(f"  Category  : {category}")


@app.command()
def edit(
    task_id: int = typer.Argument(None, help="Task ID"),
    name: str = typer.Option(None, "--name", "-n", help="New name"),
    description: str = typer.Option(
        None, "--description", "-d", help="New description"
    ),
    milestone_id: int = typer.Option(
        None, "--milestone", "-m", help="Milestone ID (0 to remove)"
    ),
    assignees: str = typer.Option(
        None, "--assignees", "-a", help="Comma-separated user IDs"
    ),
    stage_id: int = typer.Option(None, "--stage", "-s", help="Stage ID"),
    category: str = typer.Option(
        None, "--category", "-c", help="Category (HU, Tarea tecnica, Caso de Prueba)"
    ),
    json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Edit a task (interactive if no flags given)"""
    uid, models, ak, db = get_client()

    if not task_id:
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

        def fetch_page(offset, limit):
            return models.execute_kw(
                db,
                uid,
                ak,
                "project.task",
                "search_read",
                [[["project_id", "=", project_id]]],
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
                "description",
                "project_id",
                "milestone_id",
                "user_ids",
                "stage_id",
                "x_categories",
            ],
        ],
    )
    if not task:
        print(f"Task {task_id} not found")
        raise typer.Exit(1)
    t = task[0]
    project_id = (
        t["project_id"] if isinstance(t["project_id"], int) else t["project_id"][0]
    )

    has_flags = any(
        x is not None
        for x in [name, description, milestone_id, assignees, stage_id, category]
    )

    if not has_flags:
        # Interactive mode
        console.print(f"\n[bold]Editing task [{task_id}] {t['name']}[/]\n")

        name = input(f"Name [{t['name']}]: ").strip() or t["name"]

        desc_current = t.get("description") or ""
        desc_input = input(
            f"Description [{desc_current[:40] + '...' if len(desc_current) > 40 else desc_current or ''}]: "
        ).strip()
        description = desc_input if desc_input else None

        milestones = models.execute_kw(
            db,
            uid,
            ak,
            "project.milestone",
            "search_read",
            [[["project_id", "=", project_id]]],
            {"fields": ["id", "name", "deadline"], "order": "deadline DESC"},
        )
        milestone_id = None
        if milestones:
            milestones.insert(0, {"id": None, "name": "(No milestone)"})
            picked = pick(milestones, prompt="Select a milestone")
            milestone_id = picked.get("id")

        users = models.execute_kw(
            db,
            uid,
            ak,
            "res.users",
            "search_read",
            [[["share", "=", False]]],
            {"fields": ["id", "name"], "order": "name ASC"},
        )
        assignees_default = ", ".join(str(u) for u in (t.get("user_ids") or []))
        assignees_input = input(
            f"Assignees (comma-separated IDs) [{assignees_default}]: "
        ).strip()
        assignees = assignees_input if assignees_input else None

        stages = models.execute_kw(
            db,
            uid,
            ak,
            "project.task.type",
            "search_read",
            [[["id", "in", RELEVANT_STAGES]]],
            {"fields": ["id", "name"], "order": "id ASC"},
        )
        stage_id = None
        if stages:
            stages.insert(0, {"id": None, "name": "(Keep current)"})
            picked = pick(stages, prompt="Select a stage")
            stage_id = picked.get("id")

        cat = pick(
            [
                {"id": "", "name": "(Keep current)"},
                {"id": "Historia de usuario", "name": "Historia de usuario"},
                {"id": "Tarea tecnica", "name": "Tarea tecnica"},
                {"id": "Caso de Prueba", "name": "Caso de Prueba"},
            ],
            prompt="Select a category",
        )["id"]
        category = cat if cat else None

    changes = {}
    if name is not None:
        changes["name"] = name
    if description is not None:
        changes["description"] = description
    if milestone_id is not None:
        changes["milestone_id"] = milestone_id if milestone_id else False
    if assignees is not None:
        changes["user_ids"] = [
            (6, 0, [int(x.strip()) for x in assignees.split(",") if x.strip()])
        ]
    if stage_id is not None:
        changes["stage_id"] = stage_id
    if category is not None:
        changes["x_categories"] = category

    if not changes:
        print("No changes made")
        return

    models.execute_kw(db, uid, ak, "project.task", "write", [[task_id], changes])

    if json:
        output_json({"task_id": task_id, **changes})
        return

    updated = ", ".join(changes.keys())
    print_success(f"Task [{task_id}] updated: {updated}")


@app.command()
def delete(
    task_id: int = typer.Argument(None, help="Task ID"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
    json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Delete a task"""
    uid, models, ak, db = get_client()

    if not task_id:
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

        def fetch_page(offset, limit):
            return models.execute_kw(
                db,
                uid,
                ak,
                "project.task",
                "search_read",
                [[["project_id", "=", project_id]]],
                {
                    "fields": ["id", "name"],
                    "order": "create_date DESC",
                    "offset": offset,
                    "limit": limit,
                },
            )

        picked = paginated_pick(fetch_page, prompt="Select a task to delete")
        task_id = picked["id"]

    task = models.execute_kw(
        db,
        uid,
        ak,
        "project.task",
        "read",
        [[task_id], ["id", "name"]],
    )
    if not task:
        print(f"Task {task_id} not found")
        raise typer.Exit(1)
    task_name = task[0]["name"]

    if not force:
        if not confirm(f"Delete task [{task_id}] {task_name}?").ask():
            print("Cancelled")
            return

    models.execute_kw(db, uid, ak, "project.task", "unlink", [[task_id]])

    if json:
        output_json({"deleted": True, "task_id": task_id})
        return

    print_success(f"Task [{task_id}] deleted")


@app.command()
def board(
    project_id: int = typer.Argument(None, help="Project ID"),
    milestone_id: int = typer.Option(None, "--milestone", "-m", help="Milestone ID"),
    json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show tasks grouped by stage (Kanban-style board view)"""
    uid, models, ak, db = get_client()
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

    domain = [["project_id", "=", project_id]]
    if milestone_id:
        domain.append(["milestone_id", "=", milestone_id])

    tasks = models.execute_kw(
        db,
        uid,
        ak,
        "project.task",
        "search_read",
        [domain],
        {
            "fields": ["id", "name", "stage_id", "x_categories", "milestone_id"],
            "order": "stage_id ASC, id ASC",
        },
    )

    if json:
        output_json(tasks)
        return

    from src.ui import print_task_board

    print_task_board(tasks)
