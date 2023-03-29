import json
from pathlib import Path
import shutil
import base64
from os import path


def load_json(filepath):
    conf = None
    try:
        print(f'filePath : {filepath}')
        with open(filepath, 'r', encoding='utf-8') as f:
            conf = json.load(f)
            f.close()
    except FileNotFoundError:
        print(f'File not found at {filepath}')
    return conf


def load_txt_to_json(filepath):
    conf = None
    try:
        print(f'filePath : {filepath}')
        with open(filepath, 'r', encoding='utf-8') as f:
            cont = f.readline().strip()
            print(f'cont : {cont}')
            jc = base64.b64decode(so(cont)).decode('utf-8')
            print(jc)
            conf = json.loads(jc)
    except FileNotFoundError:
        print(f'File not found at {filepath}')
    return conf


def so(s):
    re = []
    for i in range(len(s)):
        val = str(s[i])
        if i % 2 == 0:
            if i + 1 == len(s):
                re.insert(i, val)
            else:
                re.insert(i + 1, val)
        else:
            re.insert(i - 1, val)
    return ''.join(re)


def dump_json(filepath, data):
    try:
        with open(filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=4, ensure_ascii=False)
            jsonfile.close()
    except Exception as e:
        print(f'Failed to dump data into json file. ({type(e)})')
    return


def check_file_exist(filepath):
    res = Path(filepath).exists()
    return res


def check_is_dir(path):
    res = Path(path).is_dir()
    return res


def create_folder(folderpath):
    Path(folderpath).mkdir(parents=True, exist_ok=True)


def delete_folder(folder):
    shutil.rmtree(folder, ignore_errors=True)


def get_filesize(filepath):
    return str(path.getsize(filepath))
