import typer
from src.client import get_client
from src.utils import output_json

app = typer.Typer(no_args_is_help=True)


@app.command()
def list(
    json: bool = typer.Option(False, '--json', help='Output as JSON'),
):
    """List all users"""
    uid, models, ak, db = get_client()
    users = models.execute_kw(db, uid, ak, 'res.users',
        'search_read', [[['share', '=', False]]], {
            'fields': ['id', 'name', 'login', 'email'],
            'order': 'name ASC',
        })
    if json:
        output_json(users)
        return
    print(f'Users ({len(users)}):\n')
    for u in users:
        print(f"  [{u['id']}] {u['name']}  |  {u.get('login', '')}")
