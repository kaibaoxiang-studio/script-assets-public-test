from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]

def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write(path, value):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix='.'+path.name,dir=path.parent)
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as f:
            json.dump(value,f,ensure_ascii=False,indent=2); f.write('\n')
        os.replace(tmp,path)
    finally:
        Path(tmp).unlink(missing_ok=True)

def inside(root, relative):
    root=Path(root).resolve(); rel=Path(relative)
    if rel.is_absolute() or '..' in rel.parts or not rel.parts:
        raise ValueError('Expected a nonempty relative path: '+str(relative))
    path=root/rel
    if not path.resolve().is_relative_to(root) or path.is_symlink():
        raise ValueError('Path escapes artifact directory: '+str(relative))
    return path

def identifier(value):
    if not isinstance(value,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:-]{0,127}',value):
        raise ValueError('Invalid identifier: '+str(value))
    return value

def validate(data, schema_name):
    from jsonschema import Draft202012Validator
    schema=read(ROOT/'schemas'/schema_name)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(data)
