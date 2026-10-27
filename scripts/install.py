#!/usr/bin/env python3
"""Install the selected public-test plugins through the supported Codex CLI."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plugins',nargs='+',choices=['screenplay-standardizer','scene-log-extractor','screenplay-asset-extractor','asset-design'])
    p.add_argument('--codex-bin',default='codex');p.add_argument('--dry-run',action='store_true')
    a=p.parse_args();codex=shutil.which(a.codex_bin)
    if not codex:p.error('Codex CLI not found; pass --codex-bin')
    market=json.loads((ROOT/'.agents/plugins/marketplace.json').read_text(encoding='utf-8'))
    chosen=a.plugins or [x['name'] for x in market['plugins']]
    commands=[[codex,'plugin','marketplace','add',str(ROOT),'--json']]
    commands += [[codex,'plugin','add',name+'@'+market['name'],'--json'] for name in chosen]
    results=[]
    if not a.dry_run:
        for command in commands:
            r=subprocess.run(command,capture_output=True,text=True)
            if r.returncode:raise SystemExit(r.stderr or r.stdout)
            results.append(json.loads(r.stdout))
    print(json.dumps({'dry_run':a.dry_run,'commands':commands,'results':results},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
