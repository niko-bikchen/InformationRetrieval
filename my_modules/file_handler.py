import os
import json
from typing import List, Any


def files_in_dir(dir_path: str) -> List[str]:
    return [fr'{dir_path}\\{item}' for item in os.listdir(fr'{dir_path}') if item.endswith('.txt')]


def write_json(file_name: str, data: Any) -> bool:
    try:
        with open(fr'{file_name}.json', 'w') as handler:
            json.dump(data, handler, sort_keys=True, indent=4)
        return True
    except IOError:
        return False


def write_txt(file_name: str, data: Any) -> bool:
    try:
        with open(fr'{file_name}.txt', 'w') as file:
            file.write(data)
        return True
    except IOError:
        return False
