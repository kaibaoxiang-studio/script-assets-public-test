#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { loadLibrary, inside, run } from './query-design.mjs';

const defaultRoot=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
export function snapshot(root=defaultRoot) {
  const walk=dir=>fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>{
    if(e.isSymbolicLink()) throw new Error('交付库不允许符号链接');
    const p=path.join(dir,e.name); return e.isDirectory()?walk(p):[p];
  }).sort();
  return walk(root).map(p=>[path.relative(root,p),crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex')]);
}
export function checkLibrary(root=defaultRoot) {
  root=path.resolve(root); const before=snapshot(root); const lib=loadLibrary(root); let checks=1;
  const ensure=(value,message)=>{if(!value) throw new Error(message);checks++;};
  for(const entry of lib.index.entries) {
    const content=lib.contents.get(entry.id);
    ensure(run(['--id',entry.id,'--read'],root).content===content,'正文读取不一致');
    ensure(JSON.stringify(run(['--id',entry.id,'--sources'],root).sources.map(s=>s.id))===JSON.stringify(entry.source_ids),'来源读取不一致');
  }
  for(const problem of lib.problems) ensure(run(['--problem',problem.id,'--read'],root).content===lib.problemContents.get(problem.id),'问题正文读取不一致');
  for(const [relative] of before) {
    ensure(['.md','.json','.mjs'].includes(path.extname(relative)),'交付格式不支持：'+relative);
    const text=fs.readFileSync(inside(root,relative),'utf8');
    if(relative.endsWith('.md')) for(const match of text.matchAll(/\]\(([^)]+)\)/g)) {
      const href=match[1].split('#')[0];
      if(!href||/^https?:\/\//.test(href)) continue;
      ensure(!path.isAbsolute(href),'文档链接须为相对路径');
      inside(root,path.normalize(path.join(path.dirname(relative),href))); checks++;
    }
  }
  ensure(JSON.stringify(before)===JSON.stringify(snapshot(root)),'通用检查不得修改交付库');
  return {passed:true,checks,entries:lib.index.entries.length,problems:lib.problems.length,sources:lib.sources.length,categories:Object.keys(lib.index.categories).length,scope:'数据与引用、案例/问题读取、库内相对链接、只读；不限首批数量，不验证艺术效果或报告真实性'};
}
if(process.argv[1]&&fs.realpathSync(process.argv[1])===fs.realpathSync(fileURLToPath(import.meta.url))) {
  try {
    if(process.argv.length>3) throw new Error('用法：node scripts/check-library.mjs [知识库目录]');
    process.stdout.write(JSON.stringify(checkLibrary(process.argv[2]??defaultRoot),null,2)+'\n');
  } catch(error) {process.stderr.write(JSON.stringify({error:error.message})+'\n');process.exitCode=1;}
}
