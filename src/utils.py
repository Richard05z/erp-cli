import json
import sys


def pick(items, label_field='name', id_field='id', prompt='Select an option'):
    if not items:
        print('No items available')
        sys.exit(1)
    if len(items) == 1:
        return items[0]
    for i, item in enumerate(items, 1):
        label = item.get(label_field, item.get('name', ''))
        extra = ''
        for f in ['deadline', 'date_start', 'create_date']:
            v = item.get(f)
            if v:
                extra += f' ({v})'
                break
        print(f'  {i}. {label}{extra}')
    while True:
        try:
            choice = int(input(f'\n{prompt} [1-{len(items)}]: '))
            if 1 <= choice <= len(items):
                return items[choice - 1]
            print(f'Enter a number between 1 and {len(items)}')
        except (ValueError, EOFError):
            print('Invalid input')


def format_m2o(field):
    if isinstance(field, list) and len(field) >= 2:
        return field[1]
    return field or ''


def output_json(data):
    print(json.dumps(data, indent=2, default=str))
