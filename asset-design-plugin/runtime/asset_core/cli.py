from __future__ import annotations
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
from .common import ROOT, read
from .project import Project

def parser():
    p=argparse.ArgumentParser(description='资产设计插件 v0.1.0 — 跨角色、场景、道具设计与可追溯交接')
    commands=p.add_subparsers(dest='command',required=True)
    commands.add_parser('doctor'); commands.add_parser('validate')
    for name in ('init','refresh-sources'):
        c=commands.add_parser(name); c.add_argument('--project',required=True,type=Path)
        c.add_argument('--script',required=True,type=Path); c.add_argument('--assets',type=Path)
    for name in ('status','index','replay','cancel','submit-context','submit-baseline','plan','import-character','register-delivery','approve-baseline','run','retry','adopt'):
        c=commands.add_parser(name); c.add_argument('--project',required=True,type=Path)
        if name in ('submit-context','submit-baseline','plan','import-character','register-delivery'): c.add_argument('--file',required=True,type=Path)
        if name in ('retry','adopt'): c.add_argument('--task',required=True)
        if name in ('adopt','approve-baseline'): c.add_argument('--statement',required=True)
        if name=='approve-baseline': c.add_argument('--revision',required=True,type=int)
        if name=='run':
            c.add_argument('--max-workers',type=int,default=3); c.add_argument('--timeout',type=int,default=600)
    return p

def main():
    args=parser().parse_args()
    try:
        if args.command in ('doctor','validate'):
            sys.path.insert(0,str(ROOT/'scripts'))
            from validate_package import validate
            result=validate(ROOT)
            if args.command=='doctor':
                executable=shutil.which('codex')
                result={'version':'0.1.0','python':sys.version.split()[0],
                    'python_supported':sys.version_info>=(3,12),'codex':executable,
                    'codex_version':subprocess.check_output([executable,'--version'],text=True).strip() if executable else None,
                    'package':result}
        else:
            project=Project(args.project); command=args.command
            if command=='init': result=project.init(args.script,args.assets)
            elif command=='refresh-sources': result=project.refresh_sources(args.script,args.assets)
            elif command=='status': result=project.status()
            elif command=='index': result=project.index()
            elif command=='replay': result=project.replay()
            elif command=='cancel': result=project.cancel()
            elif command=='submit-context': result=project.submit_context(read(args.file))
            elif command=='submit-baseline': result=project.submit_baseline(read(args.file))
            elif command=='plan': result=project.plan(read(args.file))
            elif command=='import-character': result=project.import_character(args.file)
            elif command=='register-delivery': result=project.register_delivery(read(args.file))
            elif command=='approve-baseline': result=project.approve_baseline(args.revision,args.statement)
            elif command=='retry': result=project.retry(args.task)
            elif command=='adopt': result=project.adopt(args.task,args.statement)
            elif command=='run':
                from .runner import run
                result=run(project,args.max_workers,args.timeout)
        print(json.dumps(result,ensure_ascii=False,indent=2)); return 0
    except Exception as exc:
        print(json.dumps({'status':'failed','error':str(exc)},ensure_ascii=False),file=sys.stderr); return 2
