import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { run, loadLibrary } from '../scripts/query-design.mjs';
import { snapshot } from '../scripts/check-library.mjs';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const before=snapshot(root);let checks=0;
const test=fn=>{fn();checks++;};
const first=q=>run(['--query',q,'--limit','1'],root).results[0];
for(const [q,id] of [['定稿 旧稿 覆写','DES-007'],['反打 出口','DES-008'],['晾衣杆 太小','DES-009'],['树皮 重复','DES-010'],['雨景 水路','DES-011'],['暴雨','DES-011']]) test(()=>assert.equal(first(q)?.id,id));
test(()=>assert.equal(run(['--query-problems','雨景 湿态','--limit','1'],root).results[0]?.id,'weather-water'));
test(()=>assert.equal(run(['--query-problems','版本 覆写','--limit','1'],root).results[0]?.id,'state-version'));
test(()=>assert.equal(run(['--query','不存在项目案例XYZ'],root).returned,0));
test(()=>assert.equal(run(['--category','reading','--query','反打'],root).returned,0));
const library=loadLibrary(root);
for(const e of library.index.entries.filter(e=>e.id>='DES-007')) test(()=>{
  assert(e.evidence_refs.length>0);
  assert.equal(e.verification.image_tested,false);
  assert.equal(e.verification.spatially_tested,false);
  assert.equal(e.verification.independent_reviewed,false);
  assert(!Object.hasOwn(first(e.tags[0]),'content'));
});
test(()=>{
  const sources=run(['--id','DES-010','--sources'],root).sources;
  assert.equal(sources[0].type,'local_project');assert(!Object.hasOwn(sources[0],'url'));
  const manifest=JSON.parse(fs.readFileSync(path.join(root,sources[0].manifest_path),'utf8'));
  assert.equal(manifest.documents.length,8);assert.equal(manifest.observations.length,4);
  assert(manifest.observations.every(o=>o.role==='user'));
});
test(()=>assert(run(['--id','DES-001','--sources'],root).sources[0].url.startsWith('https://')));

// 进程内覆盖检验损坏来源，不修改真实文件。
const indexPath=path.join(root,'knowledge/design/index.json');
const sourcesPath=path.join(root,'knowledge/design/sources.json');
const manifestPath=path.join(root,'knowledge/design/provenance/courtyard-case-001.json');
function corrupted(mutate) {
  const data=Object.fromEntries([indexPath,sourcesPath,manifestPath].map(p=>[p,JSON.parse(fs.readFileSync(p,'utf8'))]));
  mutate(data[indexPath],data[sourcesPath],data[manifestPath]);
  const read=fs.readFileSync;
  fs.readFileSync=function(p,...args){const v=data[path.resolve(String(p))];return v?(args[0]?JSON.stringify(v):Buffer.from(JSON.stringify(v))):read.call(this,p,...args);};
  try{assert.throws(()=>loadLibrary(root));}finally{fs.readFileSync=read;}
}
for(const mutate of [
  (i,s)=>s.sources.find(v=>v.id==='S009').manifest_path='../outside.json',
  (i,s)=>s.sources.find(v=>v.id==='S009').url='https://example.com/fake',
  (i,s,m)=>m.documents[0].sha256='invalid',
  (i,s,m)=>m.documents[0].path='../outside.md',
  (i,s,m)=>m.observations[0].log='missing.jsonl',
  (i,s,m)=>m.observations[0].role='developer',
  (i,s,m)=>m.observations[0].ordinal=-1,
  i=>i.entries.find(e=>e.id==='DES-010').evidence_refs=[{source_id:'S009',document:'missing.md',section:'test'}],
  i=>i.entries.find(e=>e.id==='DES-010').evidence_refs=[{source_id:'S009',log:'missing.jsonl',ordinal:9}],
  i=>i.entries.find(e=>e.id==='DES-010').evidence_refs=[{source_id:'S001',document:'fake',section:'test'}],
  i=>{const v=i.entries.find(e=>e.id==='DES-010').verification;v.image_tested=true;delete v.evidence;}
]) test(()=>corrupted(mutate));
test(()=>{
  const r=spawnSync(process.execPath,[path.join(root,'scripts/query-design.mjs'),'--id','DES-011','--read'],{cwd:os.tmpdir(),encoding:'utf8'});
  assert.equal(r.status,0,r.stderr);assert.equal(JSON.parse(r.stdout).entry.id,'DES-011');
});
test(()=>{
  const temp=fs.mkdtempSync(path.join(os.tmpdir(),'scene-kb-portable-'));
  try{
    fs.cpSync(root,path.join(temp,'library'),{recursive:true});
    const r=spawnSync(process.execPath,[path.join(temp,'library/scripts/query-design.mjs'),'--id','DES-010','--sources'],{cwd:temp,encoding:'utf8'});
    assert.equal(r.status,0,r.stderr);assert.equal(JSON.parse(r.stdout).sources[0].type,'local_project');
  } finally {fs.rmSync(temp,{recursive:true,force:true});}
});
test(()=>assert.deepEqual(snapshot(root),before));
process.stdout.write(JSON.stringify({passed:true,checks,scope:'项目召回、来源兼容、损坏定位拒绝、未验证状态、隔离复制与只读；不证明成图或空间效果'},null,2)+'\n');
