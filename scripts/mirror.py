#!/usr/bin/env python3
"""Validate and package the fixed public-testing snapshot without source access."""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile
import zipfile

ROOT=Path(__file__).resolve().parents[1]
TAG='public-test-2026-10-27-r4'
EXCLUDED={'.git','__pycache__','.venv','.pytest_cache','.harness','dist','reports'}

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def files(root):
    for p in sorted(Path(root).rglob('*')):
        rel=p.relative_to(root)
        if set(rel.parts)&EXCLUDED or p.suffix in ('.pyc','.pyo') or p.name=='.DS_Store':continue
        if p.is_symlink():raise ValueError('No symlinks in public snapshot: '+str(rel))
        if p.is_file():yield p,rel

def components(root):
    market=read(root/'.agents/plugins/marketplace.json')
    expected={'screenplay-standardizer':'0.1.2','scene-log-extractor':'0.1.0','screenplay-asset-extractor':'0.1.1','asset-design':'0.1.0'}
    if market['name']!='script-assets-public-test' or len(market['plugins'])!=4:raise ValueError('Wrong public marketplace')
    result=[]
    for x in market['plugins']:
        p=(root/x['source']['path']).resolve()
        if not p.is_relative_to(root.resolve()):raise ValueError('Escaping plugin path')
        manifest=read(p/'.codex-plugin/plugin.json')
        if manifest['name']!=x['name'] or manifest['version']!=expected.get(x['name']):raise ValueError('Component identity drift')
        result.append({'name':x['name'],'version':manifest['version'],'path':p.relative_to(root).as_posix()})
    if {x['name'] for x in result}!=set(expected):raise ValueError('Missing business plugin')
    return result

def validate(root=ROOT,run_components=True):
    root=Path(root).resolve();source_lock=read(root/'mirror-sources.json');count=0;changed=0
    for source in source_lock['sources']:
        base=root/source['target']
        for row in source['files']:
            p=(base/row['path']).resolve()
            if not p.is_relative_to(base.resolve()) or not p.is_file() or sha(p)!=row['export_sha256']:
                raise ValueError('Public snapshot hash mismatch: '+source['target']+'/'+row['path'])
            count+=1;changed+=row['source_sha256']!=row['export_sha256']
        for row in source.get('additions',[]):
            p=base/row['path']
            if sha(p)!=row['export_sha256']:raise ValueError('Public addition changed: '+str(p))
    # Scan content rather than filenames only; source regex literals do not match.
    forbidden=[re.compile(r'(?:gh[pousr]_[A-Za-z0-9]{24,}|sk-[A-Za-z0-9_-]{30,})'),
               re.compile(r'/Users/[A-Za-z0-9._-]+/')]
    python_count=0
    for p,rel in files(root):
        text=p.read_text(encoding='utf-8')
        if any(pattern.search(text) for pattern in forbidden):raise ValueError('Private locator or credential pattern: '+str(rel))
        if p.suffix=='.py':ast.parse(text,filename=str(rel));python_count+=1
    authority=source_lock['authoritative_capabilities']
    if authority['script_suite']['repository']!='kaibaoxiang-studio/script-plugins':raise ValueError('Wrong screenplay authority')
    expected_children={'character-assets':'0.2.13','scene-assets':'0.9.5','prop-assets':'0.2.5'}
    child_lock=read(root/'asset-design-plugin/bundle-lock.json')
    child_versions={}
    for domain,name in [('character','character-assets'),('scene','scene-assets'),('prop','prop-assets')]:
        spec=authority[domain]
        if spec['repository']!='kaibaoxiang-studio/ZiChan' or spec['commit']!=child_lock['source_commit']:
            raise ValueError('Asset ability must follow the explicit ZiChan source')
        manifest=read(root/spec['target']/'.codex-plugin/plugin.json')
        if manifest['version']!=expected_children[name] or child_lock['plugins'][name]['version']!=manifest['version']:
            raise ValueError('Public child version drift: '+name)
        child_versions[name]=manifest['version']
    comps=components(root);checks=[]
    if run_components:
        env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
        for item in comps:
            p=root/item['path'];cmd=[sys.executable,str(p/'harness.py'),'validate']
            if item['name']!='asset-design':cmd+=['--plugin',str(p)]
            result=subprocess.run(cmd,capture_output=True,text=True,env=env)
            if result.returncode:raise ValueError(item['name']+': '+result.stderr.strip())
            data=json.loads(result.stdout)
            if not data.get('valid'):raise ValueError(item['name']+': '+str(data))
            checks.append({'component':item['name'],'validation':data})
    export=read(root/'asset-design-plugin/validation/public-export-checks.json')
    if export.get('status') != 'passed' or not export.get('checks') or any(c.get('status') != 'passed' for c in export['checks']):
        raise ValueError('Current r4 validation evidence is pending or failed; record actual checks before packaging')
    return {'schema_version':'PublicMirrorValidationV1','snapshot_tag':TAG,'date':'2026-10-27',
        'valid':True,'source_files_checked':count,'documentation_and_provenance_overlays':changed,
        'python_files_parsed':python_count,'components':comps,'component_checks':checks,
        'asset_regressions':export,'credential_or_personal_source_locator_matches':0,
        'authoritative_capabilities':authority,'child_versions':child_versions,
        'business_code_changes':True,
        'business_change_source':'Canonical ZiChan character 0.2.13 update; screenplay/scene/prop business bytes unchanged.',
        'packaging_integration_changes':['asset-design-plugin/scripts/bundle.py','asset-design-plugin/scripts/validate_package.py'],
        'new_model_or_image_calls':bool(export.get('fresh_model_calls')),
        'scope':'Public export integrity, syntax, component Skill/reference validation, and documented local regression results; user business and visual testing remain the purpose of this release.'}

def archive(source,target,label):
    selected=list(files(source))
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p,rel in selected:
            i=zipfile.ZipInfo(label+'/'+rel.as_posix(),(2026,10,27,0,0,0));i.create_system=3
            i.external_attr=(stat.S_IFREG|(0o755 if p.stat().st_mode&0o111 else 0o644))<<16
            i.compress_type=zipfile.ZIP_DEFLATED;z.writestr(i,p.read_bytes())
    with zipfile.ZipFile(target) as z:
        if z.testzip():raise ValueError('Corrupt archive')
    return {'name':target.name,'sha256':sha(target),'bytes':target.stat().st_size,'files':len(selected)}

def package(root=ROOT):
    result=validate(root);write(root/'public-validation.json',result)
    out=root/'dist'/TAG;out.mkdir(parents=True,exist_ok=True);artifacts=[]
    for item in components(root):
        suffix='-public-test' if item['name']=='asset-design' else ''
        filename=item['name']+'-'+item['version']+suffix+'.zip'
        label='asset-design-plugin' if item['name']=='asset-design' else item['name']
        artifacts.append(archive(root/item['path'],out/filename,label))
    full=out/('script-assets-'+TAG+'.zip');artifacts.append(archive(root,full,'script-assets-public-test'))
    with tempfile.TemporaryDirectory(prefix='public-mirror-unpack-') as temp:
        base=Path(temp)
        with zipfile.ZipFile(full) as z:
            for i in z.infolist():
                p=base/i.filename;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(i));p.chmod(stat.S_IMODE(i.external_attr>>16))
        validate(base/'script-assets-public-test')
    manifest={'snapshot_tag':TAG,'components':components(root),'archives':artifacts,'unpacked_full_snapshot_validation':True}
    write(out/'release-manifest.json',manifest)
    checksum_targets=[out/x['name'] for x in artifacts]+[out/'release-manifest.json']
    (out/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+p.name+'\n' for p in checksum_targets),encoding='utf-8')
    return manifest

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['validate','package']);a=p.parse_args()
    try:
        result=package() if a.command=='package' else validate()
        if a.command=='validate':write(ROOT/'public-validation.json',result)
        print(json.dumps(result,ensure_ascii=False,indent=2))
    except Exception as e:raise SystemExit(str(e))
