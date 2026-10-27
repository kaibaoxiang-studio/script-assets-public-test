"""Behavioral ledger checks. No network or model calls are made by this file."""
from pathlib import Path
import copy
import json
import shutil
import sys
import tempfile
import threading
import time
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
sys.path.insert(0, str(ROOT / 'tests'))
from asset_core.project import Project, source_chunks
from helpers import FIXTURES, byte_hash, canonical_hash, character_project, write_json


class ProjectContractTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.script = self.base / 'screenplay.json'
        self.assets = self.base / 'assets.json'
        shutil.copyfile(FIXTURES / 'screenplay.json', self.script)
        shutil.copyfile(FIXTURES / 'assets.json', self.assets)
        self.project = Project(self.base / 'mother')
        self.project.init(self.script, self.assets)

    def context(self):
        state = self.project.state
        return {'schema_version': 'AssetProjectContextV1',
                'source_sha256': state['sources']['screenplay']['sha256'],
                'coverage': [x['id'] for x in state['chunks']],
                'story_summary': '林禾的保护行为反驳旁人的胆怯评价。',
                'world_rules': ['海堤旁的修理铺，暴雨和铜闸维修逻辑'],
                'cross_asset_design': ['以能握持的铜钥匙联系手部和低工作台的尺度。'],
                'evidence': [{'chunk_id': state['chunks'][-1]['id'], 'observation': '她留防水披肩给孩子并独自走入暴雨。', 'kind': 'script_fact'}],
                'hidden_information': []}

    def baseline(self):
        return {'schema_version': 'AssetVisualBibleV1',
                'context_revision': self.project.state['context']['revision'],
                'style_intent': '有岁月痕迹的电影纪实质感',
                'world_rules': ['遵守海边潮湿环境与修理行为'],
                'material_logic': ['铜表面氧化集中在凹处，布料磨损有使用依据'],
                'color_light': ['阴天冷灰漫射光中保留皮肤自然变化'],
                'symbol_language': ['弧线来自潮闸结构，避免无依据阵营徽章'],
                'domain_constraints': {'character': ['保持自然肤质'], 'scene': ['按场景插件规则设计无人修理铺'], 'prop': ['齿槽需要擦干且钥匙适合手掌握持']},
                'open_questions': []}

    def ready(self):
        self.project.submit_context(self.context())
        self.project.submit_baseline(self.baseline())
        self.project.approve_baseline(1, '测试中的用户确认：采用此项目美术方向。')

    def spec(self, tid, domain='character', asset_id='CHR-001', depends_on=None):
        return {'id': tid, 'domain': domain, 'asset_id': asset_id, 'state_id': 'S01',
                'objective': '设计与人物行为、世界和材质逻辑相符的具体文字方案。',
                'depends_on': depends_on or [], 'context': {}, 'constraints': [],
                'deliverables': ['design.md']}

    def envelope(self, status='succeeded', artifacts=None):
        return {'status': status, 'result': {'summary': '已形成具体推荐稿。',
                'design_decisions': ['以三维结构和真实材料控制视觉。'],
                'unresolved': [], 'knowledge_used': ['相关专项规范']},
                'artifacts': ['design.md'] if artifacts is None else artifacts,
                'questions': [], 'error': None}

    def run_success(self, tid):
        self.project.start_task(tid)
        directory = self.base / 'runs' / tid
        directory.mkdir(parents=True)
        artifact = directory / 'design.md'
        artifact.write_text('# 设计\n具体轮廓、连接和材质依据。\n', encoding='utf-8')
        self.project.finish(tid, self.envelope(), directory, thread_id='temporary-test-thread')
        self.project.adopt(tid, '母总控核查设计回应人物、来源及跨资产尺度。')
        return artifact

    def register(self, tid, artifact):
        spec = self.project.state['tasks'][tid]['spec']
        target = {k: spec[k] for k in ('asset_id', 'state_id', 'domain')}
        approval = {**target, 'stage': 'text_design', 'artifact_sha256': byte_hash(artifact),
                    'authority': 'user', 'statement': '用户确认此文字设计版本。'}
        path = self.base / (tid + '-approval.json')
        write_json(path, approval)
        self.project.register_delivery({**target, 'stage': 'text_design',
            'artifact_path': str(artifact), 'approval_record_path': str(path), 'task_id': tid})
        return path

    def test_full_source_coverage_and_source_version_are_required(self):
        context = self.context()
        incomplete = copy.deepcopy(context)
        incomplete['coverage'].pop()
        with self.assertRaisesRegex(ValueError, 'cover every'):
            self.project.submit_context(incomplete)
        wrong = copy.deepcopy(context)
        wrong['source_sha256'] = 'f' * 64
        with self.assertRaisesRegex(ValueError, 'source mismatch'):
            self.project.submit_context(wrong)
        self.project.submit_context(context)
        self.assertEqual(self.project.state['context']['data']['coverage'], context['coverage'])
        self.assertEqual(self.project.replay(), self.project.state)

    def test_baseline_approval_binds_current_context_revision(self):
        self.project.submit_context(self.context())
        self.project.submit_baseline(self.baseline())
        self.project.plan([self.spec('face')])
        with self.assertRaisesRegex(ValueError, 'approved current baseline'):
            self.project.ready_tasks()
        with self.assertRaises(ValueError):
            self.project.approve_baseline(99, '用户确认')
        self.project.approve_baseline(1, '用户确认')
        self.assertEqual(self.project.ready_tasks(), ['face'])
        newer = self.context()
        newer['story_summary'] += '进一步明确他人评价与实际行为的反差。'
        self.project.submit_context(newer)
        with self.assertRaisesRegex(ValueError, 'approved current baseline'):
            self.project.ready_tasks()
        self.assertTrue(self.project.state['baseline']['review_required'])

    def test_formal_assets_and_raw_provisional_ids_do_not_mix(self):
        with self.assertRaisesRegex(ValueError, 'formal asset ID'):
            self.project.plan([self.spec('wrong', 'scene', 'CHR-001')])
        raw = Project(self.base / 'raw')
        raw.init(FIXTURES / 'raw-script.md')
        with self.assertRaisesRegex(ValueError, 'tmp-'):
            raw.plan([self.spec('face')])
        raw.plan([self.spec('face', asset_id='tmp-person-001')])
        self.assertEqual(raw.state['assets'], {})
        self.assertFalse(raw.status()['formal_assets'])

    def test_invalid_asset_table_lineage_creates_no_ledger(self):
        broken = json.loads(self.assets.read_text())
        broken['source']['sha256'] = '0' * 64
        write_json(self.assets, broken)
        invalid = Project(self.base / 'invalid')
        with self.assertRaisesRegex(ValueError, 'exact screenplay'):
            invalid.init(self.script, self.assets)
        self.assertFalse(invalid.database.exists())

    def test_cycles_and_missing_dependencies_are_atomic(self):
        with self.assertRaisesRegex(ValueError, 'cycle'):
            self.project.plan([self.spec('a', depends_on=['b']), self.spec('b', depends_on=['a'])])
        self.assertEqual(self.project.state['tasks'], {})
        with self.assertRaisesRegex(ValueError, 'Missing dependency'):
            self.project.plan([self.spec('a', depends_on=['unknown'])])
        self.assertEqual(self.project.state['tasks'], {})

    def test_failure_only_blocks_dependents_and_retry_preserves_history(self):
        self.ready()
        self.project.plan([self.spec('prop', 'prop', 'PRP-001'), self.spec('face', depends_on=['prop']), self.spec('scene', 'scene', 'SCN-001')])
        self.project.start_task('prop')
        blocked = self.envelope('blocked', [])
        blocked['questions'] = ['钥匙齿结构关系影响开启方式，请确认。']
        blocked['result']['unresolved'] = blocked['questions'][:]
        self.project.finish('prop', blocked, self.base)
        self.assertEqual(self.project.ready_tasks(), ['scene'])
        with self.assertRaisesRegex(ValueError, 'successful'):
            self.project.adopt('prop', '整合采纳')
        self.project.retry('prop')
        self.assertEqual(self.project.state['tasks']['prop']['attempt'], 1)
        self.assertEqual(len(self.project.state['tasks']['prop']['history']), 1)
        self.assertEqual(set(self.project.ready_tasks()), {'prop', 'scene'})

    def test_child_artifact_paths_cannot_escape_or_be_symlinks(self):
        self.ready()
        self.project.plan([self.spec('face')])
        self.project.start_task('face')
        artifact_dir = self.base / 'artifacts'
        artifact_dir.mkdir()
        outer = self.base / 'outside.md'
        outer.write_text('outside', encoding='utf-8')
        (artifact_dir / 'link.md').symlink_to(outer)
        for relative in ('../outside.md', str(outer), 'link.md'):
            with self.subTest(relative=relative), self.assertRaises(ValueError):
                self.project.finish('face', self.envelope(artifacts=[relative]), artifact_dir)
        self.assertEqual(self.project.state['tasks']['face']['status'], 'running')

    def test_success_requires_actual_file_and_adoption_checks_its_hash(self):
        self.ready()
        self.project.plan([self.spec('face')])
        self.project.start_task('face')
        with self.assertRaisesRegex(ValueError, 'actual artifact'):
            self.project.finish('face', self.envelope(artifacts=[]), self.base)
        (self.base / 'design.md').write_text('first', encoding='utf-8')
        self.project.finish('face', self.envelope(), self.base)
        (self.base / 'design.md').write_text('unreviewed edit', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'artifact changed'):
            self.project.adopt('face', '整合检查通过')
        self.assertFalse(self.project.state['tasks']['face']['adopted'])
        self.assertEqual(self.project.index()['items'][0]['artifacts'][0]['integrity'], 'changed')

    def test_blocking_questions_or_error_cannot_be_adopted_as_success(self):
        self.ready()
        self.project.plan([self.spec('face-' + field) for field in ('questions', 'error')])
        (self.base / 'design.md').write_text('draft', encoding='utf-8')
        for field in ('questions', 'error'):
            task_id = 'face-' + field
            self.project.start_task(task_id)
            value = self.envelope()
            if field == 'questions':
                value['questions'] = ['请决定关键身份']
            else:
                value['error'] = '设计执行异常'
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.project.finish(task_id, value, self.base)

    def test_nonblocking_followup_is_preserved_without_domain_approval(self):
        self.ready()
        self.project.plan([self.spec('face')])
        self.project.start_task('face')
        (self.base / 'design.md').write_text('第一阶段可审阅推荐稿', encoding='utf-8')
        envelope = self.envelope()
        envelope['result']['unresolved'] = ['候选方向留待用户审稿时选择，当前设计阶段输出完整。']
        self.project.finish('face', envelope, self.base)
        self.project.adopt('face', '核查输出完整，保留后续用户选案事项。')
        index = self.project.index()
        self.assertEqual(index['items'][0]['unresolved'], envelope['result']['unresolved'])
        self.assertEqual(index['domain_approved_deliveries'], [])

    def test_changed_source_during_child_run_cannot_complete_as_current(self):
        self.ready()
        self.project.plan([self.spec('face')])
        self.project.start_task('face')
        (self.base / 'design.md').write_text('candidate from old source', encoding='utf-8')
        self.script.write_text(self.script.read_text() + ' ', encoding='utf-8')
        try:
            self.project.finish('face', self.envelope(), self.base)
        except ValueError:
            pass
        self.assertNotEqual(self.project.state['tasks']['face']['status'], 'succeeded')
        with self.assertRaises(ValueError):
            self.project.adopt('face', '不能采纳过时来源候选')

    def test_mother_adoption_does_not_create_domain_approval(self):
        self.ready()
        self.project.plan([self.spec('face')])
        artifact = self.run_success('face')
        task = self.project.state['tasks']['face']
        self.assertFalse(task['integration_review']['domain_approval'])
        self.assertEqual(self.project.state['deliveries'], [])
        self.register('face', artifact)
        delivery = self.project.index()['domain_approved_deliveries'][0]
        self.assertEqual(delivery['approval']['authority'], 'user')
        self.assertFalse(delivery['review_required'])
        artifact.write_text('changed after approval', encoding='utf-8')
        self.assertTrue(self.project.index()['domain_approved_deliveries'][0]['review_required'])

    def test_changed_task_invalidates_descendants_and_only_affected_deliveries(self):
        self.ready()
        specs = [self.spec('prop', 'prop', 'PRP-001'), self.spec('face', depends_on=['prop']), self.spec('scene', 'scene', 'SCN-001')]
        self.project.plan(specs)
        self.run_success('prop')
        face = self.run_success('face')
        scene = self.run_success('scene')
        self.register('face', face)
        self.register('scene', scene)
        changed = copy.deepcopy(specs[0])
        changed['objective'] += '修改握持端和钥匙齿槽的尺度。'
        self.project.plan([changed])
        tasks = self.project.state['tasks']
        self.assertEqual(tasks['prop']['status'], 'stale')
        self.assertEqual(tasks['face']['status'], 'stale')
        self.assertEqual(tasks['scene']['status'], 'succeeded')
        self.assertTrue(tasks['scene']['adopted'])
        deliveries = {d['task_id']: d for d in self.project.state['deliveries']}
        self.assertTrue(deliveries['face']['review_required'])
        self.assertFalse(deliveries['scene']['review_required'])

    def test_cancel_does_not_cancel_already_completed_work(self):
        self.ready()
        self.project.plan([self.spec('face'), self.spec('scene', 'scene', 'SCN-001')])
        self.run_success('face')
        self.project.cancel()
        self.assertEqual(self.project.ready_tasks(), [])
        self.assertEqual(self.project.state['tasks']['face']['status'], 'succeeded')
        self.assertEqual(self.project.state['tasks']['scene']['status'], 'canceled')

    def test_changed_dependency_artifact_blocks_only_its_downstream(self):
        self.ready()
        self.project.plan([self.spec('prop', 'prop', 'PRP-001'), self.spec('face', depends_on=['prop']), self.spec('scene', 'scene', 'SCN-001')])
        prop = self.run_success('prop')
        prop.write_text('unreviewed new grip design', encoding='utf-8')
        ready = self.project.ready_tasks()
        self.assertNotIn('face', ready)
        self.assertIn('scene', ready)
        with self.assertRaises(ValueError):
            self.project.start_task('face')

    def test_task_start_rechecks_baseline_inside_transaction(self):
        self.ready()
        self.project.plan([self.spec('face')])
        original_update = self.project._update
        raced = []
        def replace_before_transaction(kind, function):
            if kind == 'task_started' and not raced:
                raced.append(True)
                replacement = self.baseline()
                replacement['style_intent'] += '待确认的新冷暖方案'
                self.project.submit_baseline(replacement)
            return original_update(kind, function)
        with mock.patch.object(self.project, '_update', side_effect=replace_before_transaction):
            with self.assertRaises(ValueError):
                self.project.start_task('face')
        self.assertFalse(self.project.state['baseline']['approval'])
        self.assertNotEqual(self.project.state['tasks']['face']['status'], 'running')

    def test_scheduler_interrupt_signals_worker_before_waiting_for_it(self):
        from asset_core import runner
        self.ready()
        self.project.plan([self.spec('face')])
        started = threading.Event()
        observed = []
        def worker(project, key, timeout, canceled):
            project.start_task(key)
            started.set()
            deadline = time.monotonic() + 0.3
            while not canceled.is_set() and time.monotonic() < deadline:
                time.sleep(0.005)
            observed.append(canceled.is_set())
            project.finish(key, self.envelope('failed', []), self.base)
            return project.state['tasks'][key]['status']
        def interrupt_after_start(*args, **kwargs):
            self.assertTrue(started.wait(1))
            raise KeyboardInterrupt()
        with mock.patch.object(runner, 'execute_task', side_effect=worker), mock.patch.object(runner, 'wait', side_effect=interrupt_after_start):
            with self.assertRaises(KeyboardInterrupt):
                runner.run(self.project, max_workers=1, timeout=1)
        self.assertEqual(observed, [True])
        self.assertFalse((self.project.root / '.asset-design' / 'run.lock').exists())

    def test_imported_image_review_is_rechecked_after_import(self):
        child_path, child = character_project(self.base / 'child')
        self.project.import_character(child_path)
        review_path = child_path.parent / child['reviews']['avatar-approved']['path']
        review = json.loads(review_path.read_text())
        review['verdict'] = 'revise'
        review['blocking_issues'] = ['用户待修订']
        write_json(review_path, review)
        image = next(x for x in self.project.index()['imports'][0]['records'] if x['key'].startswith('image:'))
        self.assertTrue(image['review_required'])

    def test_valid_child_import_preserves_approval_and_source_bytes(self):
        child_path, child = character_project(self.base / 'child')
        before = {str(p.relative_to(child_path.parent)): p.read_bytes() for p in child_path.parent.rglob('*') if p.is_file()}
        self.project.import_character(child_path)
        imported = self.project.state['imports'][0]
        identity = next(x for x in imported['records'] if x['key'].startswith('stage-design:identity'))
        image = next(x for x in imported['records'] if x['key'].startswith('image:'))
        self.assertEqual(identity['approval']['operator'], 'human:original-owner')
        self.assertEqual(image['approval'], child['images'][0]['approval'])
        self.assertFalse(image['review_required'])
        self.assertEqual(before, {str(p.relative_to(child_path.parent)): p.read_bytes() for p in child_path.parent.rglob('*') if p.is_file()})
        self.assertEqual(self.project.state['deliveries'], [])

    def test_child_record_tamper_is_rejected_atomically(self):
        child_path, child = character_project(self.base / 'child')
        identity_path = child_path.parent / 'records' / 'identity.json'
        changed = json.loads(identity_path.read_text())
        changed['payload']['face'] = 'unapproved replacement'
        write_json(identity_path, changed)
        with self.assertRaisesRegex(ValueError, 'Invalid character record'):
            self.project.import_character(child_path)
        self.assertEqual(self.project.state['imports'], [])

    def test_child_source_version_mismatch_rejects_import(self):
        child_path, child = character_project(self.base / 'child')
        child['inputs']['screenplay']['sha256'] = 'f' * 64
        write_json(child_path, child)
        with self.assertRaisesRegex(ValueError, 'identical screenplay'):
            self.project.import_character(child_path)
        self.assertEqual(self.project.state['imports'], [])

    def test_child_image_review_hash_must_match_approval(self):
        child_path, child = character_project(self.base / 'child')
        child['images'][0]['approval']['review_sha256'] = '0' * 64
        write_json(child_path, child)
        with self.assertRaisesRegex(ValueError, 'lineage mismatch'):
            self.project.import_character(child_path)
        self.assertEqual(self.project.state['imports'], [])

    def test_child_review_stage_must_match_approved_image(self):
        child_path, child = character_project(self.base / 'child')
        review_path = child_path.parent / 'reviews' / 'avatar.json'
        review = json.loads(review_path.read_text())
        review['stage'] = 'execution'
        write_json(review_path, review)
        child['reviews']['avatar-approved']['sha256'] = canonical_hash(review)
        child['images'][0]['approval']['review_sha256'] = canonical_hash(review)
        write_json(child_path, child)
        with self.assertRaisesRegex(ValueError, 'review|stage'):
            self.project.import_character(child_path)
        self.assertEqual(self.project.state['imports'], [])

    def test_child_image_prompt_must_match_current_prompt_record(self):
        child_path, child = character_project(self.base / 'child')
        child['images'][0]['prompt_sha256'] = '1' * 64
        write_json(child_path, child)
        with self.assertRaisesRegex(ValueError, 'prompt|lineage'):
            self.project.import_character(child_path)
        self.assertEqual(self.project.state['imports'], [])

    def test_child_image_character_must_be_in_formal_roster(self):
        child_path, child = character_project(self.base / 'child')
        child['images'][0]['character_id'] = 'CHR-999'
        write_json(child_path, child)
        with self.assertRaisesRegex(ValueError, 'character|roster|target'):
            self.project.import_character(child_path)
        self.assertEqual(self.project.state['imports'], [])

    def test_imported_record_character_must_match_formal_roster(self):
        child_path, child = character_project(self.base / 'child')
        identity_path = child_path.parent / 'records' / 'identity.json'
        identity = json.loads(identity_path.read_text())
        identity['character_id'] = 'CHR-999'
        write_json(identity_path, identity)
        record = child['records']['stage-design:identity:CHR-001:base']
        record['sha256'] = canonical_hash(identity)
        record['approval']['sha256'] = record['sha256']
        write_json(child_path, child)
        with self.assertRaisesRegex(ValueError, 'character|roster|target'):
            self.project.import_character(child_path)
        self.assertEqual(self.project.state['imports'], [])

    def test_imported_approval_is_rechecked_when_original_file_changes(self):
        child_path, child = character_project(self.base / 'child')
        self.project.import_character(child_path)
        image_path = child_path.parent / child['images'][0]['path']
        image_path.write_bytes(b'unreviewed replacement image')
        records = self.project.index()['imports'][0]['records']
        image = next(x for x in records if x['key'].startswith('image:'))
        self.assertTrue(image['review_required'])
        self.assertEqual(image['approval'], child['images'][0]['approval'])

    def test_source_refresh_marks_existing_child_approvals_for_review(self):
        child_path, child = character_project(self.base / 'child')
        self.project.import_character(child_path)
        updated_script = json.loads(self.script.read_text())
        updated_script['title'] += '修订'
        write_json(self.script, updated_script)
        updated_assets = json.loads(self.assets.read_text())
        updated_assets['source']['sha256'] = byte_hash(self.script)
        write_json(self.assets, updated_assets)
        self.project.refresh_sources(self.script, self.assets)
        imported = self.project.index()['imports'][0]
        self.assertTrue(all(x['review_required'] for x in imported['records']))
        self.assertIsNone(self.project.state['context'])
        self.assertIsNone(self.project.state['baseline'])


if __name__ == '__main__':
    unittest.main()
