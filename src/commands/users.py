# User (res.users) commands
import typer
from src.client import get_client
from src.utils import output_json
from src.ui import print_user_table

app = typer.Typer(no_args_is_help=True)


@app.command()
def list(
    json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """List all internal users (excludes portal/public)"""
    uid, models, ak, db = get_client()
    # Filter out portal users (share=True) to show only internal team members
    users = models.execute_kw(
        db,
        uid,
        ak,
        "res.users",
        "search_read",
        [[["share", "=", False]]],
        {
            "fields": ["id", "name", "login", "email"],
            "order": "name ASC",
        },
    )
    if json:
        output_json(users)
        return
    print_user_table(users)
