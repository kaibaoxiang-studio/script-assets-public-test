"""Isolated positive/negative checks; no images, services or installed-file writes."""

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'check_skill_files.py'
SPEC = importlib.util.spec_from_file_location('check_skill_files', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class FileChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='sence-files-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'skill'
        self.root.mkdir()
        self.entry = self.root / 'SKILL.md'
        self.entry.write_text('---\nname: sence-prompts\ndescription: Test fixture\n---\n\n# 测试\n',
                              encoding='utf-8')

    def append(self, content):
        with self.entry.open('a', encoding='utf-8') as stream:
            stream.write(content)

    def test_valid_unicode_encoded_image_and_reference_links(self):
        (self.root / '参考 文件.md').write_text('# 门的取舍\n# 门的取舍\n', encoding='utf-8')
        (self.root / 'color.png').write_bytes(b'fixture')
        self.append('[门](<参考 文件.md#门的取舍-1>)\n'
                    '[编码](%E5%8F%82%E8%80%83%20%E6%96%87%E4%BB%B6.md#门的取舍)\n'
                    '![色卡](color.png)\n[参考][ref]\n[ref]: <参考 文件.md#门的取舍>\n')
        result = MODULE.check(self.root)
        self.assertTrue(result['valid'], result['errors'])
        self.assertEqual(result['local_links_checked'], 4)

    def test_missing_file_fails(self):
        self.append('[不存在](missing.md)\n')
        self.assertIn('missing link target', '\n'.join(MODULE.check(self.root)['errors']))

    def test_missing_heading_fails(self):
        self.append('[不存在](#不存在)\n')
        self.assertIn('missing heading', '\n'.join(MODULE.check(self.root)['errors']))

    def test_code_examples_and_remote_links_are_not_local_dependencies(self):
        self.append('~~~text\n# 假标题\n[示例](missing.md)\n~~~\n'
                    '`[示例](missing.md)`\n[外部](https://example.invalid/reference)\n')
        result = MODULE.check(self.root)
        self.assertTrue(result['valid'], result['errors'])
        self.assertEqual(result['remote_links_skipped'], 1)
        self.assertNotIn('假标题', MODULE.heading_ids(MODULE.without_fences(self.entry.read_text())))

    def test_heading_in_code_is_not_a_real_anchor(self):
        self.append('```md\n# 假标题\n```\n[链接](#假标题)\n')
        self.assertFalse(MODULE.check(self.root)['valid'])

    def test_link_cannot_escape_package(self):
        outside = Path(self.temp.name) / 'outside.md'
        outside.write_text('# Outside\n', encoding='utf-8')
        self.append('[外部文件](../outside.md)\n')
        self.assertIn('link outside skill', '\n'.join(MODULE.check(self.root)['errors']))

    def test_missing_frontmatter_and_entry_fail(self):
        self.entry.write_text('# Missing metadata\n', encoding='utf-8')
        self.assertFalse(MODULE.check(self.root)['valid'])
        self.entry.unlink()
        self.assertIn('Missing required SKILL.md', MODULE.check(self.root)['errors'])

    def test_empty_metadata_cannot_consume_the_next_line(self):
        self.entry.write_text('---\nname:\ndescription:\nmetadata: value\n---\n# Test\n',
                              encoding='utf-8')
        result = MODULE.check(self.root)
        self.assertFalse(result['valid'])
        self.assertIn('SKILL.md: missing name', result['errors'])
        self.assertIn('SKILL.md: missing description', result['errors'])

    def test_blank_quoted_null_and_comment_metadata_fail(self):
        for value in ('', '   ', '""', "''", '"   "', 'null', '~', '# no value', 'null # comment'):
            with self.subTest(value=value):
                self.assertFalse(MODULE.field_has_value(
                    f'name: {value}\ndescription: Valid', 'name'))

    def test_nonempty_scalar_and_block_metadata_pass(self):
        for value in ('sence-prompts', '"sence-prompts"', "'sence-prompts'", 'test # comment'):
            with self.subTest(value=value):
                self.assertTrue(MODULE.field_has_value(f'name: {value}', 'name'))
        self.assertTrue(MODULE.field_has_value('description: >-\n  Valid text\nname: test',
                                              'description'))
        self.assertFalse(MODULE.field_has_value('description: |\n\nname: test', 'description'))

    def test_backticks_in_link_destination_are_not_removed(self):
        self.append('[不存在](#`不存在`)\n')
        result = MODULE.check(self.root)
        self.assertFalse(result['valid'])
        self.assertEqual(result['heading_links_checked'], 1)
        self.assertIn('#`不存在`', '\n'.join(result['errors']))

    def test_backticks_in_filename_are_preserved(self):
        (self.root / '`notes`.md').write_text('# Notes\n', encoding='utf-8')
        self.append('[文档](`notes`.md)\n')
        result = MODULE.check(self.root)
        self.assertTrue(result['valid'], result['errors'])

    def test_code_labels_keep_links_but_code_examples_are_skipped(self):
        self.append('[查看 `文档`](SKILL.md#测试)\n'
                    '`[不是链接](missing.md)`\n'
                    '``[不是链接](missing.md) ` text``\n')
        result = MODULE.check(self.root)
        self.assertTrue(result['valid'], result['errors'])
        self.assertEqual(result['local_links_checked'], 1)

    def test_escaped_paths_and_anchors_are_decoded(self):
        (self.root / 'my_file.md').write_text('# 标题_\n', encoding='utf-8')
        (self.root / 'part(one).md').write_text('# Part\n', encoding='utf-8')
        self.append('[文档](my\\_file.md#标题\\_)\n'
                    '[括号](part\\(one\\).md)\n'
                    '[引用][ref]\n[ref]: my\\_file.md\n')
        result = MODULE.check(self.root)
        self.assertTrue(result['valid'], result['errors'])
        self.assertEqual(result['local_links_checked'], 3)

    def test_escaped_missing_target_still_fails(self):
        self.append('[不存在](missing\\_file.md)\n')
        self.assertIn('missing link target', '\n'.join(MODULE.check(self.root)['errors']))

    def test_reference_labels_normalize_internal_whitespace(self):
        self.append('[文档][my  ref]\n[my ref]: SKILL.md#测试\n')
        result = MODULE.check(self.root)
        self.assertTrue(result['valid'], result['errors'])

    def test_snapshot_change_addition_and_removal(self):
        baseline = Path(self.temp.name) / 'before'
        baseline.mkdir()
        (baseline / 'SKILL.md').write_bytes(self.entry.read_bytes())
        self.append('Changed content\n')
        (self.root / 'new.txt').write_text('new', encoding='utf-8')
        self.assertFalse(MODULE.check(self.root, baseline)['valid'])
        self.assertTrue(MODULE.check(self.root, baseline, ['SKILL.md'], ['new.txt'])['valid'])
        (baseline / 'retained.txt').write_text('retain', encoding='utf-8')
        errors = MODULE.check(self.root, baseline, ['SKILL.md'], ['new.txt'])['errors']
        self.assertIn('Removed baseline file: retained.txt', errors)

    def test_undefined_reference_fails(self):
        self.append('[缺定义][missing]\n')
        self.assertIn('undefined reference', '\n'.join(MODULE.check(self.root)['errors']))

    def test_invalid_utf8_is_reported(self):
        (self.root / 'bad.md').write_bytes(b'\xff')
        self.assertIn('Not UTF-8 Markdown: bad.md', MODULE.check(self.root)['errors'])

    def test_cli_portable_root_and_failure_status(self):
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.root)],
                                cwd=self.temp.name, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.append('[不存在](missing.md)\n')
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.root)],
                                cwd=self.temp.name, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.root / 'missing')],
                                cwd=self.temp.name, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
