#!/usr/bin/env python3
"""Portable launcher for the independently installable asset-design plugin."""
import hashlib
import importlib.util
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
if sys.version_info<(3,12):
    raise SystemExit('Python 3.12+ required. Select a compatible interpreter.')
if any(importlib.util.find_spec(name) is None for name in ('jsonschema','yaml')):
    key=hashlib.sha256((ROOT/'requirements.lock').read_bytes()).hexdigest()[:16]
    suffix=Path('Scripts/python.exe') if os.name=='nt' else Path('bin/python')
    candidates=[ROOT/'.venv'/suffix,Path.home()/'.cache/harness-runtime'/key/f'py{sys.version_info.major}{sys.version_info.minor}'/suffix]
    candidate=next((p for p in candidates if p.is_file() and p.resolve()!=Path(sys.executable).resolve()),None)
    if candidate: os.execv(str(candidate),[str(candidate),str(Path(__file__).resolve()),*sys.argv[1:]])
    raise SystemExit(f'Dependencies missing. Run: "{sys.executable}" "{ROOT / "scripts/bootstrap.py"}" --install')
sys.path.insert(0,str(ROOT/'runtime'))
from asset_core.cli import main
raise SystemExit(main())
