#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const defaultRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const fail = message => { throw new Error(message); };
const lower = s => s.toLowerCase();
const validID = s => typeof s === 'string' && /^DES-\d{3,6}$/.test(s);
const strings = (v,label) => {
  if (!Array.isArray(v) || !v.length || v.some(s => typeof s !== 'string' || !s.trim())) fail(label+'必须是非空字符串数组');
};
export function inside(root, relative) {
  if (typeof relative !== 'string' || path.isAbsolute(relative) || relative.includes('\\')) fail('库内路径无效');
  const target = fs.realpathSync(path.resolve(root, relative));
  if (!target.startsWith(fs.realpathSync(root) + path.sep)) fail('库内路径越界');
  if (!fs.statSync(target).isFile()) fail('库内路径必须指向文件');
  return target;
}
export function loadLibrary(root = defaultRoot) {
  root = path.resolve(root);
  const read = p => JSON.parse(fs.readFileSync(inside(root,p),'utf8'));
  const index = read('knowledge/design/index.json');
  const sources = read('knowledge/design/sources.json');
  if (index.schema_version !== 2 || sources.schema_version !== 1) fail('不支持的索引/来源版本');
  if (!index.categories || Array.isArray(index.categories) || typeof index.categories !== 'object' || !Object.keys(index.categories).length || Object.values(index.categories).some(s=>typeof s!=='string'||!s.trim())) fail('类别定义无效');
  if (!Array.isArray(index.entries) || !index.entries.length || !Array.isArray(sources.sources)) fail('条目/来源列表无效');
  if (!Array.isArray(index.alias_groups)) fail('同义词定义无效');
  index.alias_groups.forEach((g,i)=>strings(g,'同义词组'+i));
  const ids = new Set(), sourceIDs = new Set(), paths = new Set();
  for (const s of sources.sources) {
    if (typeof s.id !== 'string' || !/^S\d{3,6}$/.test(s.id) || sourceIDs.has(s.id)) fail('来源ID无效或重复');
    sourceIDs.add(s.id);
    for (const key of ['title','publisher','type','reviewed_on','review_scope','rights']) if(typeof s[key]!=='string'||!s[key].trim()) fail('来源'+s.id+'缺少'+key);
    if (s.type==='local_project') {
      if(s.url!==undefined) fail('本地项目来源不得伪造网页URL');
      const manifest=read(s.manifest_path);
      if(manifest.schema_version!==1 || !Array.isArray(manifest.documents) || !manifest.documents.length || !Array.isArray(manifest.logs) || !Array.isArray(manifest.observations)) fail(s.id+'本地来源清单无效');
      const safe=p=>typeof p==='string'&&p.trim()&&!path.isAbsolute(p)&&!p.includes('\\')&&!p.split('/').includes('..');
      const docs=new Set(), logs=new Set();
      for(const d of manifest.documents) {
        if(!safe(d.path)||docs.has(d.path)||! /^[a-f0-9]{64}$/.test(d.sha256??'')) fail(s.id+'文档定位或散列无效');
        docs.add(d.path);
      }
      for(const l of manifest.logs) {
        if(!safe(l.name)||logs.has(l.name)||! /^[a-f0-9]{64}$/.test(l.sha256??'')) fail(s.id+'日志定位或散列无效');
        logs.add(l.name);
      }
      for(const o of manifest.observations) if(!logs.has(o.log)||o.role!=='user'||!Number.isInteger(o.ordinal)||o.ordinal<0||!Number.isFinite(Date.parse(o.timestamp))||typeof o.excerpt!=='string'||!o.excerpt.trim()) fail(s.id+'反馈定位无效');
    } else if (new URL(s.url).protocol !== 'https:') fail('来源URL须使用https');
    strings(s.facts_checked,s.id+'事实'); strings(s.not_verified,s.id+'核对边界');
  }
  const contents = new Map();
  for (const e of index.entries) {
    if (!validID(e.id) || ids.has(e.id)) fail('案例ID无效或重复');
    ids.add(e.id);
    if (!Object.hasOwn(index.categories,e.category)) fail(e.id+'类别不存在');
    for (const key of ['title','summary','case_reference']) if(typeof e[key]!=='string'||!e[key].trim()) fail(e.id+'缺少'+key);
    for (const key of ['tags','search_terms','source_ids','prerequisites','limitations']) strings(e[key],e.id+'.'+key);
    if (e.source_ids.some(id=>!sourceIDs.has(id))) fail(e.id+'来源缺失');
    if(e.evidence_refs!==undefined) {
      if(!Array.isArray(e.evidence_refs)||!e.evidence_refs.length) fail(e.id+'证据引用无效');
      for(const ref of e.evidence_refs) {
        const source=sources.sources.find(s=>s.id===ref.source_id);
        if(!source||source.type!=='local_project'||!e.source_ids.includes(source.id)) fail(e.id+'证据来源无效');
        const manifest=read(source.manifest_path);
        if(ref.document!==undefined) {
          if(!manifest.documents.some(d=>d.path===ref.document)||typeof ref.section!=='string'||!ref.section.trim()) fail(e.id+'文档引用缺失');
        } else if(!manifest.observations.some(o=>o.log===ref.log&&o.ordinal===ref.ordinal)) fail(e.id+'日志引用缺失');
      }
    }
    if (e.entry_path !== 'knowledge/design/entries/'+e.id+'.md' || paths.has(e.entry_path)) fail(e.id+'正文路径错误或重复');
    paths.add(e.entry_path);
    const body = fs.readFileSync(inside(root,e.entry_path),'utf8');
    if (!body.startsWith('# '+e.id+' '+e.title+'\n')) fail(e.id+'正文标题与索引不一致');
    contents.set(e.id,body);
    const v=e.verification;
    if (!v || typeof v.adaptation!=='string' || typeof v.source_review_scope!=='string') fail(e.id+'验证说明缺失');
    for(const key of ['source_text_reviewed','image_tested','spatially_tested','independent_reviewed']) if(typeof v[key]!=='boolean') fail(e.id+'.'+key+'须是布尔值');
    for(const key of ['image_tested','spatially_tested','independent_reviewed']) if(v[key]) {
      const evidence=v.evidence?.[key];
      if(!evidence || typeof evidence.note!=='string' || !evidence.note.trim() || typeof evidence.report_path!=='string') fail(e.id+'.'+key+'为true时须提供证据说明与库内报告路径');
      inside(root,evidence.report_path);
    }
  }
  const problems=index.problem_library??[];
  if(!Array.isArray(problems)) fail('问题库定义无效');
  const problemIDs=new Set(), problemContents=new Map();
  for(const p of problems) {
    if(typeof p.id!=='string'||! /^[a-z][a-z0-9-]{0,63}$/.test(p.id)||problemIDs.has(p.id)) fail('问题ID无效或重复');
    problemIDs.add(p.id);
    for(const key of ['title','summary']) if(typeof p[key]!=='string'||!p[key].trim()) fail(p.id+'缺少'+key);
    strings(p.search_terms,p.id+'.search_terms'); strings(p.related_case_ids,p.id+'.related_case_ids');
    if(p.related_case_ids.some(id=>!ids.has(id))) fail(p.id+'关联案例不存在');
    if(p.resource_path!=='knowledge/design/problems/'+p.id+'.md'||paths.has(p.resource_path)) fail(p.id+'问题路径无效或重复');
    paths.add(p.resource_path);
    const body=fs.readFileSync(inside(root,p.resource_path),'utf8');
    if(!body.startsWith('# '+p.title+'\n')) fail(p.id+'问题标题不一致');
    problemContents.set(p.id,body);
  }
  return {root,index,sources:sources.sources,contents,problems,problemContents};
}
function parse(argv) {
  const o={}; const values=new Set(['--query','--query-problems','--problem','--category','--id','--limit']); const flags=new Set(['--read','--sources','--list-categories','--list-problems','--help']);
  for(let i=0;i<argv.length;i++) {
    const k=argv[i]; if(!values.has(k)&&!flags.has(k)) fail('未知参数：'+k);
    if(Object.hasOwn(o,k)) fail('重复参数：'+k);
    if(flags.has(k)) o[k]=true;
    else {const v=argv[++i]; if(!v||v.startsWith('--')||!v.trim()) fail(k+'缺少非空值'); o[k]=v.trim();}
  }
  return o;
}
export function run(argv, root=defaultRoot) {
  const o=parse(argv); const lib=loadLibrary(root); const {index,sources,contents}=lib;
  if(o['--help']||o['--list-categories']||o['--list-problems']) {
    if(Object.keys(o).length!==1) fail('帮助/类别列表不能与其他参数混用');
    if(o['--list-problems']) return {problems:lib.problems};
    return o['--help'] ? {usage:['--list-categories','--list-problems','--query-problems "词1 词2" [--limit 1..100]','--problem 问题ID [--read]','--query "词1 词2" [--category 类别] [--limit 1..100]','--category 类别 [--limit 1..100]','--id DES-001 [--read|--sources]'],method:index.retrieval} : {categories:index.categories};
  }
  if(o['--category']&&!Object.hasOwn(index.categories,o['--category'])) fail('无效类别');
  const limit=o['--limit']?Number(o['--limit']):3;
  if(o['--limit']&&(!/^\d+$/.test(o['--limit'])||!Number.isInteger(limit)||limit<1||limit>100)) fail('--limit必须为1到100的整数');
  if(o['--problem']||o['--query-problems']) {
    if(o['--id']||o['--query']||o['--category']||o['--sources']||(o['--problem']&&o['--query-problems'])) fail('问题查询不能与案例查询或来源查询混用');
    if(o['--problem']) {
      if(o['--limit']) fail('--problem不能与--limit混用');
      const problem=lib.problems.find(p=>p.id===o['--problem']);if(!problem) fail('问题不存在');
      return o['--read']?{problem,content:lib.problemContents.get(problem.id)}:{problem};
    }
    if(o['--read']) fail('问题检索不直接返回全文；使用--problem ID --read');
    const terms=[...new Set(lower(o['--query-problems']).split(/\s+/u).filter(Boolean))];
    const results=lib.problems.map(p=>{
      const fields=[['title',p.title,10],['search_terms',p.search_terms.join('\n'),8],['summary',p.summary,4]];
      const matches=terms.map(term=>{
        const candidates=[...new Set([term,...index.alias_groups.filter(g=>g.map(lower).includes(term)).flat().map(lower)])];
        let best=null;
        for(const [field,value,weight] of fields) for(const candidate of candidates) {
          const score=weight*(candidate===term?1:0.75);
          if(lower(value).includes(candidate)&&(!best||score>best.score)) best={term,matched_as:candidate,field,score};
        }
        return best;
      }).filter(Boolean);
      return {...p,matches,matched_count:matches.length,score:matches.reduce((n,m)=>n+m.score,0)};
    }).filter(p=>p.matched_count).sort((a,b)=>b.score-a.score||b.matched_count-a.matched_count||a.id.localeCompare(b.id));
    return {query:o['--query-problems'],method:'空格分词与受控同义词；问题标题10、关键词8、摘要4；OR命中；不搜索正文或推断适用性',total_matches:results.length,returned:Math.min(limit,results.length),results:results.slice(0,limit)};
  }
  if(o['--read']&&o['--sources']) fail('--read与--sources不能混用');
  if((o['--read']||o['--sources'])&&!o['--id']) fail('--read/--sources必须提供--id');
  if(o['--id']) {
    if(o['--query']||o['--category']||o['--limit']) fail('--id不能与筛选参数混用');
    if(!validID(o['--id'])) fail('无效案例ID');
    const entry=index.entries.find(e=>e.id===o['--id']); if(!entry) fail('案例不存在');
    if(o['--read']) return {entry,content:contents.get(entry.id)};
    if(o['--sources']) return {id:entry.id,sources:entry.source_ids.map(id=>sources.find(s=>s.id===id))};
    return {entry};
  }
  if(!o['--query']&&!o['--category']) fail('请提供--query、--category或--id；使用--help查看用法');
  const terms=[...new Set(lower(o['--query']??'').split(/\s+/u).filter(Boolean))];
  const groups=index.alias_groups.map(g=>g.map(lower));
  const results=index.entries.filter(e=>!o['--category']||e.category===o['--category']).map(entry=>{
    const fields=[['title',entry.title,10],['tags',entry.tags.join('\n'),8],['search_terms',entry.search_terms.join('\n'),8],['case_reference',entry.case_reference,8],['summary',entry.summary,4],['body',contents.get(entry.id),1]].map(([name,value,weight])=>({name,value:lower(value),weight}));
    const matches=terms.map(term=>{
      const expansions=[...new Set([term,...groups.filter(g=>g.includes(term)).flat()])];
      let best=null;
      for(const f of fields) for(const candidate of expansions) {
        const score=f.weight*(candidate===term?1:0.75);
        if(f.value.includes(candidate)&&(!best||score>best.score)) best={term,matched_as:candidate,field:f.name,score};
      }
      return best;
    }).filter(Boolean);
    return {...entry,matched_terms:matches.map(m=>m.term),matches,matched_count:matches.length,score:matches.reduce((n,m)=>n+m.score,0)};
  }).filter(e=>!terms.length||e.matched_count>0).sort((a,b)=>b.score-a.score||b.matched_count-a.matched_count||a.id.localeCompare(b.id));
  return {query:o['--query']??null,category:o['--category']??null,method:index.retrieval,total_matches:results.length,returned:Math.min(limit,results.length),results:results.slice(0,limit)};
}
if(process.argv[1] && fs.realpathSync(process.argv[1])===fs.realpathSync(fileURLToPath(import.meta.url))) {
  try {process.stdout.write(JSON.stringify(run(process.argv.slice(2)),null,2)+'\n');}
  catch(error) {process.stderr.write(JSON.stringify({error:error.message})+'\n');process.exitCode=1;}
}
