import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const read = rel => JSON.parse(fs.readFileSync(path.join(root, rel), 'utf8'));

function parse(args) {
  const opts = { hex: [], limit: 5, query: '', id: '', films: false, categories: false, category: '' };
  for (let i = 0; i < args.length; i++) {
    const flag = args[i];
    if (flag === '--films') { opts.films = true; continue; }
    if (flag === '--list-categories') { opts.categories = true; continue; }
    if (!['--id', '--query', '--hex', '--limit', '--category'].includes(flag) || !args[i + 1])
      throw new Error('用法：query.mjs --id 058 [--films]；或 --query 关键词／--hex #RRGGBB [--category 分类] [--limit 5]');
    const value = args[++i];
    if (flag === '--hex') {
      if (!/^#[0-9a-f]{6}$/i.test(value)) throw new Error('HEX须为 #RRGGBB');
      opts.hex.push(value.toUpperCase());
    } else if (flag === '--limit') {
      opts.limit = Number(value);
      if (!Number.isInteger(opts.limit) || opts.limit < 1 || opts.limit > 140) throw new Error('limit须为1–140');
    } else opts[flag.slice(2)] = value;
  }
  if (opts.films && !opts.id) throw new Error('--films必须配合--id');
  return opts;
}

const rgb = hex => [1, 3, 5].map(start => parseInt(hex.slice(start, start + 2), 16));
const distance = (a, b) => Math.hypot(...rgb(a).map((value, i) => value - rgb(b)[i]));

function main() {
  const opts = parse(process.argv.slice(2));
  const entries = read('index.json').entries;
  if (opts.categories) {
    console.log(JSON.stringify([...new Set(entries.map(entry => entry.category))].sort(), null, 2)); return;
  }
  if (opts.id) {
    if (!/^\d{1,3}$/.test(opts.id)) throw new Error('编号应为001–140');
    const id = opts.id.padStart(3, '0');
    const entry = entries.find(item => item.id === id);
    if (!entry) throw new Error(`未找到编号 ${id}`);
    if (opts.films && !entry.film_reference_path) {
      console.log(JSON.stringify({ id, films: [], note: '源条目没有影片采样或来源占位数据' }, null, 2)); return;
    }
    console.log(JSON.stringify(read(opts.films ? entry.film_reference_path : entry.entry_path), null, 2)); return;
  }
  if (!opts.query && !opts.hex.length && !opts.category) throw new Error('请提供查询条件，或使用--id／--list-categories');
  const terms = opts.query.toLowerCase().split(/[\s,，、;；]+/).filter(Boolean);
  const results = entries.filter(entry => !opts.category || entry.category.includes(opts.category)).map(entry => {
    const text = [entry.id, entry.name_zh, entry.name_en, entry.category, entry.summary, ...entry.tags].join(' ').toLowerCase();
    const matchedTerms = terms.filter(term => text.includes(term));
    const colorMatches = opts.hex.map(target => {
      const ranked = entry.primary_colors.map(color => ({ ...color, rgb_distance: distance(target, color.hex) }))
        .sort((a, b) => a.rgb_distance - b.rgb_distance || a.code.localeCompare(b.code));
      const match = ranked[0];
      return { requested_hex: target, code: match.code, name_zh: match.name_zh, hex: match.hex,
        rgb_distance: Number(match.rgb_distance.toFixed(2)) };
    });
    const lexicalScore = matchedTerms.length;
    const meanDistance = colorMatches.length ? colorMatches.reduce((total, match) => total + match.rgb_distance, 0) / colorMatches.length : null;
    const colorScore = meanDistance === null ? 0 : 1 - meanDistance / Math.sqrt(3 * 255 ** 2);
    return { id: entry.id, name_zh: entry.name_zh, name_en: entry.name_en, category: entry.category,
      matched_terms: matchedTerms, color_matches: colorMatches, primary_colors: entry.primary_colors,
      entry_path: entry.entry_path, score: lexicalScore + colorScore,
      score_meaning: '关键词命中数＋RGB近似分；不是艺术适配概率',
    };
  }).filter(entry => !terms.length || entry.matched_terms.length > 0)
    .sort((a, b) => b.score - a.score || a.id.localeCompare(b.id)).slice(0, opts.limit);
  console.log(JSON.stringify({ method: 'keyword_and_rgb_shortlist', query: opts.query, target_hex: opts.hex,
    notice: '候选须人工或由场景skill复核材料、身份色、光源与构图；不自动迁移原模板。', results }, null, 2));
}

try { main(); } catch (error) { console.error(error.message); process.exitCode = 1; }
