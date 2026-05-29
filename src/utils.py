import json
import sys
from questionary import select, Choice


def pick(items, label_field='name', id_field='id', prompt='Select an option'):
    if not items:
        print('No items available')
        sys.exit(1)
    if len(items) == 1:
        return items[0]
    choices = []
    for item in items:
        label = item.get(label_field, '')
        extra = ''
        for f in ['deadline', 'date_start', 'create_date']:
            v = item.get(f)
            if v:
                extra += f' ({v})'
                break
        choices.append(Choice(title=f'{label}{extra}', value=item))
    return select(prompt, choices=choices).ask()


def format_m2o(field):
    if isinstance(field, list) and len(field) >= 2:
        return field[1]
    return field or ''


def output_json(data):
    print(json.dumps(data, indent=2, default=str))
