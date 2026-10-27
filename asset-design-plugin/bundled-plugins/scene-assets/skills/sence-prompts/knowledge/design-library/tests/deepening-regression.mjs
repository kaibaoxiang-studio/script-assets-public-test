import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { run, loadLibrary } from '../scripts/query-design.mjs';
import { checkLibrary, snapshot } from '../scripts/check-library.mjs';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const before=snapshot(root);let checks=0;
const test=fn=>{fn();checks++;};
const search=q=>run(['--query-problems',q,'--limit','100'],root);
const first=q=>search(q).results[0];
test(()=>assert(checkLibrary(root).passed));
for(const [q,id] of [['锚点 换视角','staging-anchors'],['特征点 主形','form-identity'],['材质 工艺','material-craft'],['配色 光域','color-light'],['失败 复测','failure-validation'],['定位点','staging-anchors']]) test(()=>assert.equal(first(q)?.id,id));
test(()=>assert.equal(search('不存在问题XYZ').returned,0));
test(()=>assert.equal(search('世界工艺未知').returned,0)); // 方法正文不参与检索。
test(()=>assert(!Object.hasOwn(first('材质'),'content')));
test(()=>assert(search('灰扑扑').results.some(p=>p.id==='color-light')));
const library=loadLibrary(root);
for(const p of library.problems) test(()=>{
  assert.equal(run(['--problem',p.id,'--read'],root).content,library.problemContents.get(p.id));
  assert(p.related_case_ids.every(id=>library.index.entries.some(e=>e.id===id)));
});
test(()=>assert.equal(run(['--list-problems'],root).problems.length,library.problems.length));
test(()=>assert.equal(run(['--query-problems','锚点','--limit','1'],root).returned,1));
test(()=>{
  const r=spawnSync(process.execPath,[path.join(root,'scripts/query-design.mjs'),'--problem','material-craft','--read'],{cwd:os.tmpdir(),encoding:'utf8'});
  assert.equal(r.status,0,r.stderr);assert.equal(JSON.parse(r.stdout).problem.id,'material-craft');
});
for(const args of [['--problem','../GUIDE.md'],['--problem','missing'],['--problem','staging-anchors','--limit','1'],['--problem','staging-anchors','--id','DES-001'],['--problem','staging-anchors','--query-problems','锚点'],['--query-problems','锚点','--category','sacred'],['--query-problems','锚点','--query','锚点'],['--query-problems','锚点','--sources'],['--query-problems','锚点','--read'],['--query-problems','锚点','--limit','0'],['--list-problems','--read']]) test(()=>assert.throws(()=>run(args,root)));

// 原索引的进程内覆盖，不修改真实目录或写入合成设计案例。
const original=JSON.parse(fs.readFileSync(path.join(root,'knowledge/design/index.json'),'utf8'));
function withIndex(index,fn) {
  const target=path.join(root,'knowledge/design/index.json'),read=fs.readFileSync;
  fs.readFileSync=function(p,...args){return path.resolve(String(p))===target?(args[0]?JSON.stringify(index):Buffer.from(JSON.stringify(index))):read.call(this,p,...args);};
  try{return fn();}finally{fs.readFileSync=read;}
}
test(()=>{
  const index=structuredClone(original);delete index.problem_library;
  withIndex(index,()=>{assert.equal(loadLibrary(root).problems.length,0);assert.equal(run(['--query-problems','锚点'],root).returned,0);assert.equal(run(['--id','DES-001'],root).entry.id,'DES-001');});
});
for(const mutate of [i=>i.problem_library.push(structuredClone(i.problem_library[0])),i=>i.problem_library[0].related_case_ids=['DES-999999'],i=>i.problem_library[0].resource_path='../GUIDE.md',i=>i.problem_library[0].title='索引标题不匹配',i=>i.problem_library[0].search_terms=[],i=>i.problem_library={}]) test(()=>{
  const index=structuredClone(original);mutate(index);withIndex(index,()=>assert.throws(()=>loadLibrary(root)));
});
test(()=>assert.deepEqual(snapshot(root),before));
process.stdout.write(JSON.stringify({passed:true,checks,scope:'问题检索/零命中/非全文、关联与全文读取、CLI跨目录、参数拒绝、旧索引兼容、损坏数据拒绝与只读；不证明艺术效果'},null,2)+'\n');
