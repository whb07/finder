from pathlib import Path
from dataclasses import dataclass
from typing import List, Union
import re
import itertools





@dataclass
class File:
    name: str
    imports: list
    
    def __repr__(self):
        return f"File({self.name})"

@dataclass
class Module:
    name: str
    contents: list

    def __repr__(self):
        return f"Module({self.name})"

    def owns_file(self, filename:str)->bool:
        return bool(list(self.filter_filename(filename)))

    def filter_filename(self, filename):
        name = filename
        if "<" in name:
            name = name.replace("<", "").replace(">", "")
        return filter(lambda n: n.name.endswith(name), self.contents)

    def get_file(self, filename:str) -> Union[None, File]:
        return next(iter(self.filter_filename(filename)), None)
    
    def list_files(self):
        return list(filter(lambda n: isinstance(n, File), self.contents))

    def list_dirs(self):
        return list(filter(lambda n: isinstance(n, Module), self.contents))
    
    def owner(self, filename):
        if self.owns_file(filename):
            return self
        result = filter(lambda n: n is not None, map(lambda n: n.owner(filename), self.list_dirs()))
        return next(iter(result), None)


def serialized(directory):
    path = Path(directory)
    if not path.is_dir():
        return [str(path.name)]

    result = {}
    files = []
    for content in path.iterdir():
        serial = serialized(content)
        if isinstance(serial, list):
            files.extend(serial)
        else:
            files.append(serial)

    result[str(path)] = files
    return result

def get_all_files(name):
    if "bitcoin/src" not in name:
        raise TypeError("only for bitcoin project")
    return serialized(name)

def get_all_files(name):
    if "bitcoin/src" not in name:
        raise TypeError("only for bitcoin project")
    return serialized(name)

def import_headers(filecontent:str):
    headers = [f for f in filecontent.split("\n") if "#include" in f]
    def clean_up(head):
        regex = r"#include (<|\").*(>|\")"
        string = head.strip()
        found = list(re.finditer(regex, string))
        if found:
            import_string = string[found[0].start():found[0].end()].split(" ")[-1].replace('"', "")
            return [import_string]
        return []
    
    return list(itertools.chain(*list(map(clean_up, headers))))

def get_file(filename)->File:
    path = Path(filename)
    if not path.is_file():
        raise TypeError("Requires a file")
    try:
        imports = import_headers(path.read_text())
    except  Exception as err:
        imports = []

    return File(name=str(filename), imports=imports)


def get_module(module_dict:dict)->Module:
    if not isinstance(module_dict, dict):
        raise TypeError("requires directory dict")
    
    path = Path(list(module_dict.keys())[0])
    if not path.is_dir():
        raise TypeError("Requires a directory")
    
    mod = Module(name=str(path), contents=[])
    
    for key, val in module_dict.items():
        for n in val:
            if isinstance(n, str):
                mod.contents.append(get_file(Path(key)/n))
            else:
                mod.contents.append(get_module(n))

    return mod


