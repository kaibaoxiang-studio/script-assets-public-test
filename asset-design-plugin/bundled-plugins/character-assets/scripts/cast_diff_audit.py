#!/usr/bin/env python3
"""Report textual cast-design overlaps without claiming a visual judgement."""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
import re

AXES = ("silhouette", "face_structure", "body_posture", "hair_structure", "costume_color")
UNKNOWN = {"", "待定", "待细化", "未知", "无资料", "未定", "n/a", "na", "not applicable"}


def normalize(value):
    if not isinstance(value, str):
        return ""
    return re.sub(r"\s+", "", value.strip().casefold())


def usable(value):
    key = normalize(value)
    return bool(key) and key not in UNKNOWN and not key.startswith(("待定:", "待定：", "不适用"))


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def project_plan(root):
    root = Path(root).expanduser().resolve()
    state = read_json(root / "project.json")
    record = state.get("records", {}).get("cast-plan")
    if not record:
        raise ValueError("Project has no submitted cast plan")
    path = root / record["path"]
    plan = read_json(path)
    by_id = {row.get("id"): row for row in plan.get("characters", [])}
    for key, card_record in state.get("records", {}).items():
        parts = key.split(":")
        if len(parts) != 3 or parts[0] != "design-card" or parts[2] != "base":
            continue
        if not card_record.get("approval") or card_record.get("stale"):
            continue
        card = read_json(root / card_record["path"])
        if card.get("schema_version") not in {"CharacterDesignCardV2", "CharacterDesignCardV2.1"}:
            continue
        row = by_id.get(parts[1])
        if row is not None and isinstance(card.get("recognition_axes"), dict):
            row["recognition_axes"] = card["recognition_axes"]
            row["axis_source"] = "approved_design_card"
    return plan, str(path), bool(record.get("approval"))


def audit(data, source, approved=False):
    if data.get("schema_version") not in {"CastPlanV1", "CastPlanV2"}:
        raise ValueError("Expected CastPlanV1 or CastPlanV2")
    characters = data.get("characters")
    if not isinstance(characters, list):
        raise ValueError("Cast plan has no characters list")
    rows, repeated_descriptions = [], {}
    for character in characters:
        ident = character.get("id")
        if not isinstance(ident, str) or not ident.strip():
            raise ValueError("Every cast row needs an id")
        axes = character.get("recognition_axes") or {}
        if not isinstance(axes, dict):
            raise ValueError(f"recognition_axes must be an object: {ident}")
        na = [key for key in AXES if normalize(axes.get(key)).startswith(("不适用:", "不适用：")) and
              character.get("morphology") in {"nonhuman", "group"}]
        missing = [key for key in AXES if not usable(axes.get(key)) and key not in na]
        description = normalize(character.get("design_distinction"))
        if description:
            repeated_descriptions.setdefault(description, []).append(ident)
        rows.append({"id": ident, "axis_source": character.get("axis_source", "cast_plan"),
                     "recognition_axes": {key: axes.get(key, "") for key in AXES},
                     "missing_or_pending_axes": missing, "not_applicable_axes": na,
                     "design_distinction": character.get("design_distinction", "")})
    pairs = []
    for left, right in itertools.combinations(rows, 2):
        shared = [key for key in AXES if usable(left["recognition_axes"].get(key)) and
                  normalize(left["recognition_axes"].get(key)) ==
                  normalize(right["recognition_axes"].get(key))]
        if len(shared) >= 2:
            pairs.append({"ids": [left["id"], right["id"]], "exact_shared_axes": shared,
                          "review_note": "文本字段相同；需由设计师并排核对，不能据此断言两人视觉撞型"})
    repeated = [{"ids": ids, "description": description}
                for description, ids in repeated_descriptions.items() if len(ids) > 1]
    report = {
        "schema_version": "CastDifferentiationAuditV1", "source": source,
        "cast_plan_approved": approved, "character_count": len(rows),
        "axes": list(AXES), "rows": rows,
        "exact_overlap_candidates": pairs, "repeated_distinctions": repeated,
        "missing_axis_characters": [row["id"] for row in rows if row["missing_or_pending_axes"]],
        "limits": ["只比较文本字段的明确相同值，近义描述和实际成图仍需人工并排审查",
                   "美型分布、年龄可信度、文化准确性和皮肤真实度不能由本脚本判定"],
    }
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--cast-plan", type=Path)
    group.add_argument("--project-root", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.project_root:
        data, source, approved = project_plan(args.project_root)
    else:
        data, source, approved = read_json(args.cast_plan), str(args.cast_plan.resolve()), False
    report = audit(data, source, approved)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output.resolve()),
                      "characters": report["character_count"],
                      "missing_axis_characters": len(report["missing_axis_characters"]),
                      "exact_overlap_candidates": len(report["exact_overlap_candidates"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
