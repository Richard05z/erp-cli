# Rich-based UI helpers for formatted CLI output
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from src.utils import format_m2o

console = Console()

STAGE_STYLES = {
    156: "bold blue",
    143: "bold yellow",
    144: "bold magenta",
    145: "bold cyan",
    146: "bold red",
    161: "bold green",
}


def _stage_style(stage_id):
    if isinstance(stage_id, list) and len(stage_id) >= 2:
        stage_id = stage_id[0]
    return STAGE_STYLES.get(stage_id, "")


def _styled_stage(stage_id):
    name = format_m2o(stage_id)
    style = _stage_style(stage_id)
    if style and name:
        return f"[{style}]{name}[/]"
    return name


def print_task_table(tasks, title=None):
    table = Table(title=title, box=box.ROUNDED)
    table.add_column("ID", style="cyan", justify="right", no_wrap=True)
    table.add_column("Name")
    table.add_column("Stage")
    table.add_column("Category")
    table.add_column("Milestone")

    for t in tasks:
        table.add_row(
            str(t["id"]),
            t["name"],
            _styled_stage(t.get("stage_id")),
            t.get("x_categories", "") or "",
            format_m2o(t.get("milestone_id")) or "",
        )

    console.print(table)


def print_task_detail(task):
    lines = []
    for label, key in [
        ("Project", "project_id"),
        ("Milestone", "milestone_id"),
        ("Category", "x_categories"),
        ("Assignees", "user_ids"),
        ("Created", "create_date"),
    ]:
        val = task.get(key)
        if key in ("project_id", "milestone_id"):
            val = format_m2o(val)
        elif key == "user_ids":
            val = str(val or [])
        elif key == "x_categories":
            val = val or ""
        lines.append(f"  {label:<12}: {val}")

    stage_name = format_m2o(task.get("stage_id"))
    style = _stage_style(task.get("stage_id"))
    stage_line = (
        f"  Stage       : [{style}]{stage_name}[/]"
        if style and stage_name
        else f"  Stage       : {stage_name}"
    )
    lines.insert(2, stage_line)

    desc = task.get("description", "")
    if desc:
        lines.append(f"\n  Description:\n  {desc}")

    panel = Panel(
        "\n".join(lines),
        title=f"[bold cyan]Task [{task['id']}] {task['name']}[/]",
        border_style="cyan",
    )
    console.print(panel)


def print_project_table(projects):
    table = Table(title=f"Projects ({len(projects)})", box=box.ROUNDED)
    table.add_column("ID", style="cyan", justify="right", no_wrap=True)
    table.add_column("Name")
    table.add_column("User")
    table.add_column("Stage")

    for p in projects:
        table.add_row(
            str(p["id"]),
            p["name"],
            format_m2o(p.get("user_id")),
            format_m2o(p.get("stage_id")),
        )

    console.print(table)


def print_milestone_table(milestones):
    table = Table(title=f"Milestones ({len(milestones)})", box=box.ROUNDED)
    table.add_column("ID", style="cyan", justify="right", no_wrap=True)
    table.add_column("Name")
    table.add_column("Project")
    table.add_column("Start")
    table.add_column("Deadline")
    table.add_column("Reached", justify="center")
    table.add_column("Tasks", justify="center")

    for m in milestones:
        reached = "[green]Yes[/]" if m.get("is_reached") else "[red]No[/]"
        tasks_str = f"{m.get('done_task_count', 0)}/{m.get('task_count', 0)}"
        table.add_row(
            str(m["id"]),
            m["name"],
            format_m2o(m.get("project_id")),
            m.get("start_date", "") or "",
            m.get("deadline", "") or "",
            reached,
            tasks_str,
        )

    console.print(table)


def print_stage_list(stages):
    console.print(f"[bold]Stages ({len(stages)})[/bold]\n")
    for s in stages:
        style = _stage_style(s["id"])
        if style:
            console.print(f"  [{style}]\\[{s['id']}] {s['name']}[/]")
        else:
            console.print(f"  [{s['id']}] {s['name']}")


def print_user_table(users):
    table = Table(title=f"Users ({len(users)})", box=box.ROUNDED)
    table.add_column("ID", style="cyan", justify="right", no_wrap=True)
    table.add_column("Name")
    table.add_column("Login")
    table.add_column("Email")

    for u in users:
        table.add_row(
            str(u["id"]),
            u["name"],
            u.get("login", ""),
            u.get("email", "") or "",
        )

    console.print(table)


def print_success(message):
    console.print(f"[green]{message}[/green]")
