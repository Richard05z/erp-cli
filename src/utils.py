import json
import sys
from questionary import select, Choice, confirm


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
    return select(prompt, choices=choices, use_search_filter=True, use_jk_keys=False, instruction='(Type to filter, use arrows to navigate)').ask()


def paginated_pick(fetch_page, label_field='name', id_field='id', prompt='Select an option', page_size=30):
    offset = 0
    while True:
        items = fetch_page(offset, page_size + 1)
        has_more = len(items) > page_size
        if has_more:
            items = items[:page_size]
        if not items:
            print('No items available')
            sys.exit(1)
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
        if has_more:
            choices.append(Choice(title='(Show more...)', value='__more__'))
        result = select(prompt, choices=choices, use_search_filter=True, use_jk_keys=False, instruction='(Type to filter, use arrows to navigate)').ask()
        if result is None:
            sys.exit(0)
        if result == '__more__':
            offset += page_size
            continue
        return result


def paginated_display(fetch_page, display_fn, page_size=30):
    offset = 0
    while True:
        items = fetch_page(offset, page_size + 1)
        has_more = len(items) > page_size
        if has_more:
            items = items[:page_size]
        if not items:
            if offset == 0:
                print('No items')
            break
        display_fn(items, offset)
        if not has_more:
            break
        offset += page_size
        try:
            if not confirm("Show more?").ask():
                break
        except (KeyboardInterrupt, EOFError):
            break


def format_m2o(field):
    if isinstance(field, list) and len(field) >= 2:
        return field[1]
    return field or ''


def output_json(data):
    print(json.dumps(data, indent=2, default=str))
