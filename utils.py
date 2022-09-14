import json
from pathlib import Path


def file_exist_and_touch(file):
    path = Path(file)

    if not path.is_file():
        print(f'The file `{path.resolve()}` does not exist ({path.parent})', end=' ')
        path.parent.resolve().mkdir(parents=True, exist_ok=True)
        path.resolve().touch()
        print(f'touch file `{path.resolve()}`', end=' ')
        with open(path, 'w') as f:
            json.dump({}, f, ensure_ascii=False, indent=1)
        print(f'Create empty json.')
    else:
        # print(f'The file `{path.resolve()}` exists')
        pass


def load(file):
    file_exist_and_touch(file)
    with open(file, 'r') as f:
        data = json.load(f)
    return data


def save(data, file):
    with open(file, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)


def get_name(user_json):
    name = ''
    if 'first_name' in user_json and len(user_json['first_name']) > 0:
        name += f"*{user_json['first_name']}*"
    if 'last_name' in user_json and len(user_json['last_name']) > 0:
        if len(name) > 0:
            name += ' '
        name += f"*{user_json['last_name']}*"
    if 'username' in user_json and len(user_json['username']) > 0:
        if len(name) > 0:
            name += f" (`{user_json['username']}`)"
        else:
            name += f"*{user_json['username']}*"
    return name
