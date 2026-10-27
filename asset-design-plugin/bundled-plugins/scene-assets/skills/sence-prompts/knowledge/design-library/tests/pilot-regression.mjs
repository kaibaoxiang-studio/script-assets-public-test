import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { run, loadLibrary } from '../scripts/query-design.mjs';
import { checkLibrary, snapshot } from '../scripts/check-library.mjs';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const before=snapshot(root); let checks=0;
const test=fn=>{fn();checks++;};
const first=(term,category)=>run(['--query',term,...(category?['--category',category]:[]),'--limit','1'],root).results[0];
test(()=>assert(checkLibrary(root).passed));
for(const [term,category,id] of [['视觉中心','sacred','DES-001'],['转折','sacred','DES-002'],['对置','assembly','DES-003'],['高位','assembly','DES-004'],['任务光','reading','DES-005'],['材质 工艺','reading','DES-006'],['大理石','reading','DES-006'],['平级 协商','assembly','DES-003'],['商议','assembly','DES-003']]) test(()=>assert.equal(first(term,category)?.id,id));
test(()=>assert(run(['--query','锚点','--limit','100'],root).results.some(e=>e.id==='DES-001')));
test(()=>assert(run(['--query','定位点','--limit','100'],root).results.some(e=>e.id==='DES-001')));
test(()=>assert.equal(first('卷边','sacred').matches.find(m=>m.term==='卷边').field,'body'));
test(()=>assert.equal(first('Commons Chamber').id,'DES-003'));
test(()=>assert.equal(run(['--query','不存在词XYZ'],root).returned,0));
test(()=>assert.equal(run(['--category','sacred','--query','相向席位'],root).returned,0));
test(()=>assert(!Object.hasOwn(first('主位'),'content')));
for(const args of [[],['--unknown'],['--query'],['--query',' '],['--id','../../GUIDE.md'],['--id','DES-999999'],['--category','no'],['--limit','0','--query','圣堂'],['--limit','1.5','--query','圣堂'],['--limit','101','--query','圣堂'],['--read'],['--sources'],['--read','--sources','--id','DES-001'],['--id','DES-001','--query','圣堂'],['--query','圣堂','--query','主位'],['--list-categories','--query','圣堂'],['--help','--id','DES-001']]) test(()=>assert.throws(()=>run(args,root)));
test(()=>assert.equal(run(['--category','sacred','--limit','100'],root).returned,Math.min(100,loadLibrary(root).index.entries.filter(e=>e.category==='sacred').length)));
test(()=>{
  const r=spawnSync(process.execPath,[path.join(root,'scripts/query-design.mjs'),'--id','DES-001'],{cwd:os.tmpdir(),encoding:'utf8'});
  assert.equal(r.status,0,r.stderr); assert.equal(r.stderr,''); assert.equal(JSON.parse(r.stdout).entry.id,'DES-001');
});
test(()=>{
  const r=spawnSync(process.execPath,[path.join(root,'scripts/query-design.mjs'),'--id','../bad'],{encoding:'utf8'});
  assert.equal(r.status,1); assert.equal(r.stdout,''); assert(JSON.parse(r.stderr).error);
});

// 进程内文件覆盖用于验证合法扩容/损坏数据，不写入真实目录。
const originalIndex=JSON.parse(fs.readFileSync(path.join(root,'knowledge/design/index.json'),'utf8'));
function overlay(index, extra, fn) {
  const data=new Map([[path.join(root,'knowledge/design/index.json'),JSON.stringify(index)],...Object.entries(extra).map(([p,text])=>[path.join(root,p),text])]);
  const originals={read:fs.readFileSync,real:fs.realpathSync,stat:fs.statSync};
  fs.readFileSync=function(p,...args){const absolute=path.resolve(String(p)); return data.has(absolute)?(args[0]?data.get(absolute):Buffer.from(data.get(absolute))):originals.read.call(this,p,...args);};
  fs.realpathSync=function(p,...args){const absolute=path.resolve(String(p));return data.has(absolute)?absolute:originals.real.call(this,p,...args);};
  fs.statSync=function(p,...args){const absolute=path.resolve(String(p));return data.has(absolute)?{isFile:()=>true}:originals.stat.call(this,p,...args);};
  try{return fn();}finally{fs.readFileSync=originals.read;fs.realpathSync=originals.real;fs.statSync=originals.stat;}
}
test(()=>{
  const index=structuredClone(originalIndex);
  index.categories.test_added='测试新增类别';
  const entry=structuredClone(index.entries[0]); const taken=new Set(index.entries.map(e=>e.id));
  let n=7; while(taken.has('DES-'+String(n).padStart(3,'0'))) n++;
  entry.id='DES-'+String(n).padStart(3,'0');entry.title='测试扩容条目';entry.category='test_added';entry.entry_path='knowledge/design/entries/'+entry.id+'.md';entry.search_terms=['扩容测试'];
  index.entries.push(entry);
  overlay(index,{[entry.entry_path]:'# '+entry.id+' '+entry.title+'\n测试数据；不是设计案例。\n'},()=>{assert.equal(loadLibrary(root).index.entries.length,originalIndex.entries.length+1);assert.equal(first('扩容测试','test_added').id,entry.id);});
});
test(()=>{
  const index=structuredClone(originalIndex); const v=index.entries[0].verification;
  for(const key of ['image_tested','spatially_tested','independent_reviewed']) v[key]=true;
  v.evidence=Object.fromEntries(['image_tested','spatially_tested','independent_reviewed'].map(key=>[key,{note:'合成验证状态测试；不表示真实出图或实测。',report_path:'tests/mock-evidence.md'}]));
  overlay(index,{'tests/mock-evidence.md':'合成证据，不代表实际评测。'},()=>assert(loadLibrary(root).index.entries[0].verification.image_tested));
});
for(const corrupt of [i=>i.entries.push(structuredClone(i.entries[0])),i=>i.entries[0].source_ids=['S999999'],i=>i.entries[0].entry_path='../GUIDE.md',i=>{i.entries[0].verification.image_tested=true;delete i.entries[0].verification.evidence;},i=>i.entries[0].verification.image_tested='true',i=>i.entries[0].verification.evidence={image_tested:{note:'test',report_path:'missing.md'}}]) test(()=>{
  const index=structuredClone(originalIndex);corrupt(index);
  if(index.entries[0].verification.evidence) index.entries[0].verification.image_tested=true;
  overlay(index,{},()=>assert.throws(()=>loadLibrary(root)));
});
test(()=>assert.deepEqual(snapshot(root),before));
process.stdout.write(JSON.stringify({passed:true,checks,scope:'首批召回与排序、正文/同义词补检、CLI、异常输入、进程内合法扩容与验证升级、损坏数据拒绝、只读；不含艺术效果验证'},null,2)+'\n');
