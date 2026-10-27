"""Event-backed project ledger. Creative judgments are supplied by the Skills.

An integration adoption never means a domain design or image is approved.
SQLite transactions keep concurrent task receipts and change events coherent.
"""
from __future__ import annotations
import copy
import json
from pathlib import Path
import sqlite3
import uuid
from .common import ROOT, now, read, write, sha, digest, inside, identifier, validate

DOMAINS={'character':'characters','scene':'locations','prop':'props'}

def source_chunks(script):
    path=Path(script); raw=path.read_text(encoding='utf-8')
    try:
        data=json.loads(raw)
    except json.JSONDecodeError:
        data=None
    units=[]
    if isinstance(data,dict) and isinstance(data.get('episodes'),list):
        # The complete episode, including summaries and scene blocks, is kept.
        for i,ep in enumerate(data['episodes']):
            units.append((f'episode-{i+1:04d}',json.dumps(ep,ensure_ascii=False,indent=2)))
        front={k:v for k,v in data.items() if k!='episodes'}
        if front: units.insert(0,('front-matter',json.dumps(front,ensure_ascii=False,indent=2)))
    else:
        units=[('source',raw)]
    chunks=[]
    for key,text in units:
        for offset in range(0,len(text),12000):
            part=text[offset:offset+12000]
            chunks.append({'id':f'{key}:{offset//12000+1}','text':part,
                           'sha256':digest(part),'start_offset':offset})
    if not chunks: raise ValueError('Empty screenplay')
    return chunks

def prepare_sources(root,script,assets=None):
    script=Path(script).resolve()
    if script.suffix.lower() not in {'.json','.md','.markdown','.txt'}:
        raise ValueError('Use standardized JSON or UTF-8 Markdown/TXT screenplay')
    chunks=source_chunks(script)
    result={'screenplay':{'path':str(script),'sha256':sha(script)},'asset_table':None}
    roster={}; relations=[]
    if assets:
        assets=Path(assets).resolve(); data=read(assets)
        if data.get('source',{}).get('sha256')!=result['screenplay']['sha256']:
            raise ValueError('Asset table must reference this exact screenplay SHA256')
        result['asset_table']={'path':str(assets),'sha256':sha(assets)}
        for domain,key in DOMAINS.items():
            for item in data.get(key,[]):
                asset_id=identifier(item['id'])
                if asset_id in roster: raise ValueError('Duplicate asset ID: '+asset_id)
                roster[asset_id]={'id':asset_id,'domain':domain,'name':item['name'],
                    'states':[s['id'] for s in item.get('states',[])],
                    'source_record':item,'source_record_sha256':digest(item),'formal':True}
        # Co-presence is evidence of a relation candidate, never proof of contact.
        memberships={}
        for asset_id,item in roster.items():
            scenes={e.get('scene_id') for e in item['source_record'].get('evidence',[]) if e.get('scene_id')}
            for s in item['source_record'].get('states',[]): scenes.update(s.get('scenes',[]))
            for scene in scenes: memberships.setdefault(scene,set()).add(asset_id)
        for scene,ids in sorted(memberships.items()):
            ids=sorted(ids)
            for i,a in enumerate(ids):
                for b in ids[i+1:]:
                    if roster[a]['domain']!=roster[b]['domain']:
                        relations.append({'from':a,'to':b,'kind':'co_presence_candidate',
                                          'scene_id':scene,'confirmed_interaction':False})
    return result,chunks,roster,relations

class Project:
    def __init__(self,path):
        self.root=Path(path).resolve(); self.database=self.root/'.asset-design/ledger.sqlite3'

    def _connect(self):
        if not self.database.exists(): raise FileNotFoundError('Initialize project first: '+str(self.root))
        c=sqlite3.connect(self.database,timeout=30); c.execute('PRAGMA foreign_keys=ON')
        return c

    @property
    def state(self):
        with self._connect() as c:
            row=c.execute('SELECT state FROM project WHERE id=1').fetchone()
            if row is None: raise ValueError('No project state')
            return json.loads(row[0])

    def _update(self,kind,fn):
        with self._connect() as c:
            c.execute('BEGIN IMMEDIATE')
            state=json.loads(c.execute('SELECT state FROM project WHERE id=1').fetchone()[0])
            result=fn(state)
            event={'type':kind,'at':now(),'state':state}
            c.execute('INSERT INTO events(type,at,payload) VALUES(?,?,?)',
                      (kind,event['at'],json.dumps(event,ensure_ascii=False)))
            c.execute('UPDATE project SET state=? WHERE id=1',(json.dumps(state,ensure_ascii=False),))
        return result if result is not None else self.state

    def init(self,script,assets=None):
        if self.database.exists(): raise FileExistsError('Project already initialized')
        sources,chunks,roster,relations=prepare_sources(self.root,script,assets)
        self.database.parent.mkdir(parents=True,exist_ok=True)
        state={'schema_version':'AssetProjectLedgerV1','id':'project-'+uuid.uuid4().hex[:12],
            'version':'0.1.0','created_at':now(),'sources':sources,'chunks':chunks,'assets':roster,
            'relations':relations,'context':None,'context_history':[],'baseline':None,'baseline_history':[],
            'tasks':{},'deliveries':[],'imports':[],'conflicts':[],'cancel_requested':False}
        with sqlite3.connect(self.database) as c:
            c.execute('CREATE TABLE project(id INTEGER PRIMARY KEY CHECK(id=1),state TEXT NOT NULL)')
            c.execute('CREATE TABLE events(seq INTEGER PRIMARY KEY AUTOINCREMENT,type TEXT,at TEXT,payload TEXT)')
            c.execute('INSERT INTO project VALUES(1,?)',(json.dumps(state,ensure_ascii=False),))
            c.execute('INSERT INTO events(type,at,payload) VALUES(?,?,?)',
                      ('initialized',now(),json.dumps({'state':state},ensure_ascii=False)))
        write(self.root/'sources/chunks.json',{'source_sha256':sources['screenplay']['sha256'],'chunks':chunks})
        return self.status()

    def check_sources(self,state=None):
        state=state or self.state
        for item in state['sources'].values():
            if item and (not Path(item['path']).is_file() or sha(item['path'])!=item['sha256']):
                raise ValueError('Source changed or missing; refresh-sources before continuing: '+item['path'])

    def _invalidate(self,s,ids,reason):
        affected=set(ids)
        while True:
            more={k for k,v in s['tasks'].items() if affected.intersection(v['spec']['depends_on'])}
            if more.issubset(affected): break
            affected.update(more)
        for key in affected:
            task=s['tasks'][key]
            if task['status']!='pending': task['status']='stale'
            task['adopted']=False; task['review_reason']=reason
        for delivery in s['deliveries']:
            if delivery.get('task_id') in affected or any(
                delivery['asset_id']==s['tasks'][key]['spec']['asset_id'] and
                delivery['state_id']==s['tasks'][key]['spec']['state_id'] for key in affected):
                delivery['review_required']=True; delivery['review_reason']=reason
        affected_assets={s['tasks'][key]['spec']['asset_id'] for key in affected}
        for imported in s['imports']:
            for record in imported['records']:
                if record.get('asset_id') in affected_assets:
                    record['review_required']=True; record['review_reason']=reason
        return sorted(affected)

    def refresh_sources(self,script,assets=None):
        sources,chunks,roster,relations=prepare_sources(self.root,script,assets)
        def change(s):
            if sources==s['sources']: return
            self._invalidate(s,list(s['tasks']),'source_version_changed')
            for d in s['deliveries']: d['review_required']=True
            for imported in s['imports']:
                imported['review_required']=True
                for record in imported['records']:
                    record['review_required']=True; record['review_reason']='source_version_changed'
            if s['context']: s['context_history'].append(s['context'])
            if s['baseline']: s['baseline_history'].append(s['baseline'])
            s.update(sources=sources,chunks=chunks,assets=roster,relations=relations,context=None,baseline=None)
        result=self._update('sources_refreshed',change)
        write(self.root/'sources/chunks.json',{'source_sha256':sources['screenplay']['sha256'],'chunks':chunks})
        return result

    def submit_context(self,data):
        validate(data,'AssetProjectContextV1.schema.json'); self.check_sources()
        def change(s):
            if data['source_sha256']!=s['sources']['screenplay']['sha256']: raise ValueError('Context source mismatch')
            expected={c['id'] for c in s['chunks']}
            if set(data['coverage'])!=expected or len(data['coverage'])!=len(expected):
                raise ValueError('Context must cover every source chunk exactly once')
            for e in data['evidence']:
                if e['chunk_id'] not in expected: raise ValueError('Unknown evidence chunk')
            prior=s['context']
            if prior and prior['sha256']==digest(data): return
            if prior: s['context_history'].append(prior)
            revision=1+max([x['revision'] for x in s['context_history']],default=0)
            s['context']={'revision':revision,'sha256':digest(data),'data':data,'at':now()}
            self._invalidate(s,list(s['tasks']),'project_context_changed')
            if s['baseline']: s['baseline']['review_required']=True
        return self._update('context_submitted',change)

    def submit_baseline(self,data):
        validate(data,'AssetVisualBibleV1.schema.json'); self.check_sources()
        def change(s):
            if not s['context'] or data['context_revision']!=s['context']['revision']:
                raise ValueError('Baseline must reference the current full-script context')
            prior=s['baseline']
            if prior and prior['sha256']==digest(data): return
            if prior: s['baseline_history'].append(prior)
            revision=1+max([x['revision'] for x in s['baseline_history']],default=0)
            s['baseline']={'revision':revision,'sha256':digest(data),'data':data,'approval':None,'review_required':False}
            self._invalidate(s,list(s['tasks']),'project_visual_baseline_changed')
        return self._update('baseline_submitted',change)

    def approve_baseline(self,revision,statement):
        if not statement.strip(): raise ValueError('Record the actual user confirmation')
        self.check_sources()
        def change(s):
            b=s['baseline']
            if not b or b['revision']!=revision or b.get('review_required'):
                raise ValueError('Approve only the current valid baseline revision')
            b['approval']={'authority':'user','statement':statement,'at':now(),'sha256':b['sha256']}
        return self._update('baseline_approved',change)

    def plan(self,data):
        if isinstance(data,list): data={'tasks':data}
        validate(data,'DomainTaskPlanV1.schema.json'); self.check_sources()
        def change(s):
            incoming={}
            for spec in data['tasks']:
                spec=copy.deepcopy(spec)
                for k,default in [('depends_on',[]),('context',{}),('constraints',[]),('deliverables',[])]: spec.setdefault(k,default)
                identifier(spec['id']); identifier(spec['asset_id']); identifier(spec['state_id'])
                if spec['id'] in incoming: raise ValueError('Duplicate task ID')
                asset=s['assets'].get(spec['asset_id'])
                if s['sources']['asset_table']:
                    if not asset or asset['domain']!=spec['domain']: raise ValueError('Task must preserve formal asset ID and domain')
                    if spec['state_id'] not in asset['states'] and asset['states']:
                        raise ValueError('Unknown formal asset state: '+spec['state_id'])
                elif not spec['asset_id'].startswith('tmp-'):
                    raise ValueError('Raw-script work uses tmp- provisional IDs')
                prior=s['tasks'].get(spec['id'])
                incoming[spec['id']]=spec
                if prior and prior['spec']!=spec:
                    if prior['status']=='running': raise ValueError('Cannot edit a running task')
                    self._invalidate(s,[spec['id']],'task_design_changed')
                if not prior:
                    s['tasks'][spec['id']]={'spec':spec,'status':'pending','attempt':0,'adopted':False,'history':[]}
                else: prior['spec']=spec
            visited=set(); active=set()
            def visit(key):
                if key in active: raise ValueError('Dependency cycle: '+key)
                if key in visited: return
                if key not in s['tasks']: raise ValueError('Missing dependency: '+key)
                active.add(key)
                for dep in s['tasks'][key]['spec']['depends_on']: visit(dep)
                active.remove(key); visited.add(key)
            for key in s['tasks']: visit(key)
        return self._update('tasks_planned',change)

    def ready_tasks(self):
        s=self.state; self.check_sources(s)
        if not s['context'] or not s['baseline'] or not s['baseline']['approval'] or s['baseline'].get('review_required'):
            raise ValueError('Full context and approved current baseline required')
        if s['cancel_requested']: return []
        changed=[k for k,t in s['tasks'].items() if t['status']=='succeeded' and t['adopted'] and
                 any(not Path(a['path']).is_file() or sha(a['path'])!=a['sha256'] for a in t.get('receipt',{}).get('artifacts',[]))]
        if changed:
            self._update('adopted_artifacts_changed',lambda current:self._invalidate(current,changed,'adopted_artifact_changed'))
            s=self.state
        return [k for k,v in s['tasks'].items() if v['status']=='pending' and all(
            s['tasks'][d]['status']=='succeeded' and s['tasks'][d]['adopted'] for d in v['spec']['depends_on'])]

    def start_task(self,key):
        if key not in self.ready_tasks(): raise ValueError('Task dependencies or approvals not ready: '+key)
        def change(s):
            t=s['tasks'][key]
            if t['status']!='pending': raise ValueError('Task already claimed')
            self.check_sources(s)
            b=s['baseline']
            if not b or not b['approval'] or b.get('review_required') or b['data']['context_revision']!=s['context']['revision'] or s['cancel_requested']:
                raise ValueError('Current baseline or scheduler state changed before task start')
            for dep in t['spec']['depends_on']:
                upstream=s['tasks'][dep]
                if upstream['status']!='succeeded' or not upstream['adopted']:
                    raise ValueError('Dependency changed before task start')
                if any(not Path(a['path']).is_file() or sha(a['path'])!=a['sha256'] for a in upstream['receipt']['artifacts']):
                    raise ValueError('Dependency artifact changed before task start')
            t.update(status='running',attempt=t['attempt']+1,started_at=now(),
                basis={'context_sha256':s['context']['sha256'],'baseline_sha256':s['baseline']['sha256'],
                       'source_sha256':s['sources']['screenplay']['sha256']})
            return copy.deepcopy(t)
        return self._update('task_started',change)

    def finish(self,key,envelope,artifact_dir,thread_id=None):
        validate(envelope,'DomainResultV1.schema.json')
        if envelope['status']=='succeeded' and (envelope['questions'] or envelope['error'] is not None):
            raise ValueError('A successful task cannot contain blocking questions or an execution error')
        try: self.check_sources(); source_current=True
        except ValueError: source_current=False
        artifacts=[]; directory=Path(artifact_dir).resolve()
        for relative in envelope['artifacts']:
            path=inside(directory,relative)
            if not path.is_file(): raise ValueError('Missing child artifact: '+relative)
            artifacts.append({'path':str(path),'sha256':sha(path),'relative_path':relative})
        if envelope['status']=='succeeded' and not artifacts: raise ValueError('Successful design requires an actual artifact')
        def change(s):
            t=s['tasks'][key]
            if t['status']!='running': raise ValueError('Task is not running')
            current={'context_sha256':s['context']['sha256'] if s['context'] else None,
                     'baseline_sha256':s['baseline']['sha256'] if s['baseline'] else None,
                     'source_sha256':s['sources']['screenplay']['sha256']}
            valid=current==t['basis'] and source_current and not s['cancel_requested']
            receipt={'at':now(),'envelope':envelope,'artifacts':artifacts,'thread_id':thread_id,
                     'ephemeral':bool(thread_id),'basis':t['basis'],'attempt':t['attempt']}
            t['history'].append(receipt); t['receipt']=receipt
            t['status']=envelope['status'] if valid else ('canceled' if s['cancel_requested'] else 'stale')
            t['adopted']=False
        return self._update('task_finished',change)

    def adopt(self,key,statement):
        if not statement.strip(): raise ValueError('Record integration review and its basis')
        self.check_sources()
        def change(s):
            t=s['tasks'][key]
            if t['status']!='succeeded': raise ValueError('Only successful current results can be adopted')
            for a in t['receipt']['artifacts']:
                if not Path(a['path']).is_file() or sha(a['path'])!=a['sha256']: raise ValueError('Child artifact changed')
            t['adopted']=True; t['integration_review']={'at':now(),'statement':statement,
                'authority':'mother_integration','domain_approval':False}
        return self._update('task_adopted',change)

    def retry(self,key):
        def change(s):
            t=s['tasks'][key]
            if t['status'] not in {'failed','blocked','stale','canceled'}: raise ValueError('Retry requires an incomplete task')
            if s['sources']['asset_table']:
                asset=s['assets'].get(t['spec']['asset_id'])
                if not asset or asset['domain']!=t['spec']['domain']:
                    raise ValueError('Task asset no longer exists in the current source version')
            t['status']='pending'; t['adopted']=False; s['cancel_requested']=False
        return self._update('task_retried',change)

    def cancel(self):
        def change(s):
            s['cancel_requested']=True
            for t in s['tasks'].values():
                if t['status']=='pending': t['status']='canceled'
        return self._update('cancel_requested',change)

    def register_delivery(self,data):
        validate(data,'DeliveryRegistrationV1.schema.json'); self.check_sources()
        artifact=Path(data['artifact_path']).resolve(); approval_path=Path(data['approval_record_path']).resolve()
        approval=read(approval_path)
        if not artifact.is_file() or approval.get('artifact_sha256')!=sha(artifact):
            raise ValueError('Approval must bind the exact artifact hash')
        for key in ('asset_id','state_id','domain','stage'):
            if approval.get(key)!=data[key]: raise ValueError('Approval target mismatch: '+key)
        if approval.get('authority')!='user' or not approval.get('statement','').strip():
            raise ValueError('A real user approval record is required')
        def change(s):
            a=s['assets'].get(data['asset_id'])
            if s['sources']['asset_table'] and (not a or a['domain']!=data['domain']): raise ValueError('Unknown asset')
            if a and a['states'] and data['state_id'] not in a['states']: raise ValueError('Unknown state')
            task_id=data.get('task_id')
            if not task_id or task_id not in s['tasks']: raise ValueError('Delivery must reference a task')
            t=s['tasks'][task_id]
            if t['status']!='succeeded' or not t['adopted']: raise ValueError('Delivery task must be adopted and current')
            if any(t['spec'][k]!=data[k] for k in ('asset_id','state_id','domain')): raise ValueError('Task target mismatch')
            s['deliveries'].append({**data,'artifact_path':str(artifact),'sha256':sha(artifact),
                'approval_record_path':str(approval_path),'approval_sha256':sha(approval_path),
                'approval':approval,'review_required':False,'at':now()})
        return self._update('domain_delivery_registered',change)

    def import_character(self,file):
        file=Path(file).resolve(); child=read(file); self.check_sources(); s=self.state
        if child.get('schema_version',child.get('schema'))!='CharacterProjectV1': raise ValueError('Expected CharacterProjectV1')
        inputs=child.get('inputs',{})
        def resolve(p): return Path(p) if Path(p).is_absolute() else file.parent/p
        for key in ('screenplay','asset_table'):
            item=inputs.get(key); expected=s['sources'].get(key)
            if not item or not expected or item.get('sha256')!=expected['sha256']:
                raise ValueError('Import requires identical screenplay and asset table versions')
            if not resolve(item['path']).is_file() or sha(resolve(item['path']))!=item['sha256']:
                raise ValueError('Imported source changed')
        roster=child.get('roster',[])
        rows=roster.values() if isinstance(roster,dict) else roster
        for row in rows:
            cid=row.get('id',row.get('character_id'))
            if cid and (cid not in s['assets'] or s['assets'][cid]['domain']!='character'):
                raise ValueError('Imported character ID is not in current formal roster: '+cid)
            if cid and row.get('asset_digest') and row['asset_digest']!=s['assets'][cid]['source_record_sha256']:
                raise ValueError('Imported character roster record differs from current asset table')
        valid_ids={x['id'] for x in (roster.values() if isinstance(roster,dict) else roster)}
        validated=[]
        for key,record in child.get('records',{}).items():
            path=resolve(record['path'])
            if not path.is_file() or digest(read(path))!=record['sha256']: raise ValueError('Invalid character record: '+key)
            payload=read(path); cid=payload.get('character_id')
            if cid and cid not in valid_ids: raise ValueError('Unknown imported record character ID: '+cid)
            approval=record.get('approval')
            if approval and approval.get('sha256')!=record['sha256']: raise ValueError('Character approval hash mismatch')
            validated.append({'key':key,'path':str(path),'sha256':record['sha256'],
                              'hash_kind':'canonical_json','asset_id':cid,
                              'approval':approval,'review_required':bool(record.get('stale'))})
        images=child.get('images',[])
        for image in images.values() if isinstance(images,dict) else images:
            if image.get('character_id') not in valid_ids:
                raise ValueError('Unknown imported image character ID')
            path=resolve(image['path'])
            if not path.is_file() or sha(path)!=image['sha256']: raise ValueError('Imported image changed')
            approval=image.get('approval')
            if approval:
                review=child.get('reviews',{}).get(image['id'])
                if not review: raise ValueError('Approved image has no review')
                rpath=resolve(review['path']); rdata=read(rpath)
                if digest(rdata)!=review['sha256'] or rdata.get('image_sha256')!=image['sha256'] or rdata.get('verdict')!='pass':
                    raise ValueError('Invalid image review')
                if rdata.get('stage')!=image['stage']: raise ValueError('Image review stage mismatch')
                if approval.get('image_sha256')!=image['sha256'] or approval.get('review_sha256')!=review['sha256']:
                    raise ValueError('Image approval lineage mismatch')
                prompt_key=f"prompt-package:{image['stage']}:{image['character_id']}:{image.get('variant_id') or 'base'}"
                prompt=child.get('records',{}).get(prompt_key)
                if not prompt or prompt['sha256']!=image.get('prompt_sha256') or not prompt.get('approval') or prompt.get('stale'):
                    raise ValueError('Image prompt lineage mismatch')
                if image.get('purpose','production')!='production': raise ValueError('Preview images cannot be imported as approved anchors')
                validated.append({'key':'review:'+image['id'],'path':str(rpath),'sha256':review['sha256'],
                    'hash_kind':'canonical_json','asset_id':image['character_id'],
                    'approval':copy.deepcopy(approval),'review_required':bool(image.get('stale'))})
            validated.append({'key':'image:'+image['id'],'path':str(path),'sha256':image['sha256'],
                'hash_kind':'bytes','asset_id':image['character_id'],
                'approval':approval,'review_required':bool(image.get('stale'))})
        snapshot={'source_path':str(file),'sha256':sha(file),'domain':'character','at':now(),
                  'approval_authority':'original_child_records','records':validated,'project':child}
        def change(state): state['imports'].append(snapshot)
        return self._update('character_project_imported',change)

    def status(self):
        s=self.state
        try: self.check_sources(s); source_status='current'
        except ValueError: source_status='changed'
        return {'project_id':s['id'],'source_status':source_status,'formal_assets':bool(s['sources']['asset_table']),
            'assets':len(s['assets']),'context_revision':s['context']['revision'] if s['context'] else None,
            'baseline_revision':s['baseline']['revision'] if s['baseline'] else None,
            'baseline_approved':bool(s['baseline'] and s['baseline']['approval'] and not s['baseline'].get('review_required')),
            'tasks':{k:{'status':v['status'],'adopted':v['adopted'],'domain':v['spec']['domain'],
                      'asset_id':v['spec']['asset_id']} for k,v in s['tasks'].items()},
            'delivery_count':len(s['deliveries']),'cancel_requested':s['cancel_requested']}

    def index(self):
        s=self.state; items=[]
        for key,task in s['tasks'].items():
            spec=task['spec']; receipt=task.get('receipt',{})
            artifacts=[]
            for a in receipt.get('artifacts',[]):
                artifacts.append({**a,'integrity':'current' if Path(a['path']).is_file() and sha(a['path'])==a['sha256'] else 'changed'})
            items.append({'task_id':key,**{k:spec[k] for k in ('domain','asset_id','state_id','depends_on')},
                'status':task['status'],'integration_adopted':task['adopted'],'artifacts':artifacts,
                'unresolved':receipt.get('envelope',{}).get('result',{}).get('unresolved',[]),
                'review_reason':task.get('review_reason'),'attempt':task['attempt'],
                'basis':task.get('basis'),'child':receipt.get('child')})
        deliveries=copy.deepcopy(s['deliveries'])
        for d in deliveries:
            if not Path(d['artifact_path']).is_file() or sha(d['artifact_path'])!=d['sha256'] or not Path(d['approval_record_path']).is_file() or sha(d['approval_record_path'])!=d['approval_sha256']:
                d['review_required']=True; d['review_reason']='delivery_or_approval_file_changed'
        imports=copy.deepcopy(s['imports'])
        for imported in imports:
            project_file=Path(imported['source_path'])
            project_changed=not project_file.is_file() or sha(project_file)!=imported['sha256']
            for record in imported['records']:
                path=Path(record['path'])
                try: actual=digest(read(path)) if record.get('hash_kind')=='canonical_json' else sha(path)
                except (OSError,ValueError): actual=None
                if actual!=record['sha256'] or project_changed:
                    record['review_required']=True; record['review_reason']='imported_source_or_record_changed'
            affected={r.get('asset_id') for r in imported['records'] if r['review_required']}
            for record in imported['records']:
                if record['key'].startswith('image:') and record.get('asset_id') in affected:
                    record['review_required']=True; record['review_reason']='imported_approval_dependency_changed'
        result={'schema_version':'UnifiedAssetIndexV1','project_id':s['id'],'source_versions':s['sources'],
                'status':self.status(),'items':items,'domain_approved_deliveries':deliveries,
                'relationships':s['relations'],'imports':imports,'conflicts':s['conflicts']}
        write(self.root/'deliverables/asset-index.json',result)
        lines=['# 统一资产索引','',f"项目：{s['id']}",'','| 任务 | 领域 | 资产 / 状态 | 状态 | 整合采纳 | 文件 |','|---|---|---|---|---|---|']
        for item in items:
            links='、'.join(f"[{Path(a['path']).name}]({Path(a['path']).as_uri()})" for a in item['artifacts'])
            lines.append(f"| {item['task_id']} | {item['domain']} | {item['asset_id']} / {item['state_id']} | {item['status']} | {item['integration_adopted']} | {links} |")
        lines+=['','整合采纳不代表单项设计或图片已获用户批准。正式批准见 JSON 的 domain_approved_deliveries；原子插件批准见 imports。']
        (self.root/'deliverables/asset-index.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
        return result

    def replay(self):
        with self._connect() as c:
            events=[json.loads(row[0]) for row in c.execute('SELECT payload FROM events ORDER BY seq')]
        return events[-1]['state'] if events else None
