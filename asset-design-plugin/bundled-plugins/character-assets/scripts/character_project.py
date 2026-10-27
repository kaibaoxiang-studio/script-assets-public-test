#!/usr/bin/env python3
"""Deterministic project state for the character-assets Codex plugin.

Creative judgements and image review belong to the Skills. This module owns
imports, lineage, approvals, invalidation and release gates.
"""
from __future__ import annotations

import argparse
import contextlib
import copy
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
from types import SimpleNamespace
import xml.etree.ElementTree as ET
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import phased_design as phased
import ensemble_assets as ensemble

SCHEMA = "CharacterProjectV1"
PLUGIN_VERSION = json.loads((Path(__file__).resolve().parents[1] / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))["version"]
IDENTITY_STAGES = ("avatar", "expression", "full_body")
STAGES = (*IDENTITY_STAGES, "costume_design", "execution")
LEGACY_STAGES = (*IDENTITY_STAGES, "execution")
V3_STAGES = (*IDENTITY_STAGES, "execution")
HEAVY_TIERS = {"主角", "重要角色"}
SUPPORTED_INPUTS = {".json", ".md", ".markdown", ".txt", ".xlsx"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
RECOGNITION_AXES = ("silhouette", "face_structure", "body_posture",
                    "hair_structure", "costume_color")
DETAIL_FIELDS = {
    "face": ("contour", "brow_eyes", "nose_mouth"),
    "hair": ("hairline_part", "volume_flow", "length_texture_color"),
    "body": ("frame_proportions", "weight_posture"),
    "skin": ("tone_variation", "surface_distribution"),
    "costume": ("silhouette_layers", "neckline", "shoulder_sleeve",
                "seams_fastening_mobility", "material_drape_wear", "color_placement"),
    "adornments": ("head_neck", "body_hands"),
}
SPECIALIST_DOMAINS = ("character-hair-design", "character-body-design",
                      "character-face-design", "character-face-signature-design",
                      "character-skin-design", "character-costume-style-design",
                      "character-costume-cut-design", "character-costume-color-design",
                      "character-costume-material-design", "character-costume-accessory-design")
SPECIALIST_DOMAINS_V22 = ("character-feature-focus", *SPECIALIST_DOMAINS)
SPECIALIST_DOMAINS_V24 = ("character-world-appearance-design", *SPECIALIST_DOMAINS_V22,
                          "character-face-decoration-design")
VISIBLE_VIEWS = {"front", "side", "back", "avatar", "full_body"}
BODY_PROPORTION_POINTS = {
    "head_body": (("头",), ("足", "脚", "身高", "全高")),
    "shoulder_hip": (("肩",), ("胯", "髋", "骨盆")),
    "torso_legs": (("裆", "臀"), ("足", "脚", "踝", "腿")),
    "arm_segments": (("肘",), ("腕",)),
    "leg_segments": (("膝",), ("踝", "足", "脚")),
}
MODEL_CARD_ATTIRE = {
    "avatar": {
        "face_only": ("服装不入画",),
        "white_tank": ("白色纯色背心",),
        "white_sports_tank": ("白色运动背心",),
    },
    "expression": {
        "face_only": ("服装不入画",),
        "white_tank": ("白色纯色背心",),
        "white_sports_tank": ("白色运动背心",),
    },
    "full_body": {
        "white_tank_shorts_barefoot": ("白色纯色背心", "短裤", "赤脚"),
        "white_sports_tank_black_shorts_barefoot":
            ("白色运动背心", "黑色运动短裤", "赤脚"),
    },
}
SPECIALIST_FIELD_DOMAINS = {
    "character-world-appearance-design": {"face", "hair", "body", "skin", "costume", "adornments"},
    "character-face-decoration-design": {"face", "skin", "adornments"},
    "character-hair-design": {"hair"}, "character-body-design": {"body"},
    "character-face-design": {"face"},
    "character-face-signature-design": {"face", "hair", "adornments"},
    "character-skin-design": {"skin"},
    "character-costume-style-design": {"costume"},
    "character-costume-cut-design": {"costume"},
    "character-costume-color-design": {"costume"},
    "character-costume-material-design": {"costume"},
    "character-costume-accessory-design": {"costume", "adornments"},
}
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
      "p": "http://schemas.openxmlformats.org/package/2006/relationships"}


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def _runtime():
    return SimpleNamespace(**globals())


def digest(data):
    if isinstance(data, Path):
        h = hashlib.sha256()
        with data.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()
    return hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent,
                                     prefix=".tmp-", delete=False) as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
        temp = Path(stream.name)
    os.replace(temp, path)


def ensure(condition, message):
    if not condition:
        raise ValueError(message)


def safe_id(value):
    ensure(bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}", value or "")),
           f"Unsafe identifier: {value!r}")
    return value


def safe_asset_label(value):
    """Keep the readable asset name while preventing path or control-character injection."""
    label = re.sub(r'[\\/:*?"<>|\x00-\x1f]+', "_", str(value or ""))
    label = re.sub(r"\s+", "_", label).strip(" ._")[:60]
    return label or "未命名资产"


def pipeline_stages(state):
    version = state.get("pipeline_version", 1)
    return V3_STAGES if version >= 3 else STAGES if version == 2 else LEGACY_STAGES


def image_predecessors(state, stage):
    version = state.get("pipeline_version", 1)
    if version >= 3:
        return {"avatar": (), "expression": ("avatar",),
                "full_body": ("avatar", "expression"),
                "execution": IDENTITY_STAGES}[stage]
    if version == 2:
        return {"avatar": (), "expression": ("avatar",),
                "full_body": ("avatar", "expression"),
                "costume_design": IDENTITY_STAGES,
                "execution": (*IDENTITY_STAGES, "costume_design")}[stage]
    return {"avatar": (), "expression": ("avatar",),
            "full_body": ("avatar",), "execution": IDENTITY_STAGES}[stage]


def variant_name(state, character_id, variant_id):
    row = next((x for x in state["roster"] if x["id"] == character_id), None)
    ensure(row is not None, f"Unknown character ID: {character_id}")
    if variant_id == "base":
        return "基础形象"
    variant = next((x for x in row.get("states", []) if x.get("id") == variant_id), None)
    return (variant.get("name") or variant_id) if variant else variant_id


def require_known_variant(state, character_id, variant_id):
    variant_name(state, character_id, variant_id)
    if variant_id != "base":
        row = next(x for x in state["roster"] if x["id"] == character_id)
        ensure(any(x.get("id") == variant_id for x in row.get("states", [])),
               f"Variant {variant_id} is absent from asset-table states")


def require_list(obj, key):
    ensure(isinstance(obj.get(key), list), f"{key} must be a list")


def require_text(obj, key):
    ensure(isinstance(obj.get(key), str) and obj[key].strip(), f"{key} must be text")


def validate_visual_details(data):
    """Require drawable decisions for newly authored human detail cards.

    This is a structural gate, not a claim that the prose or generated image is good.
    Previously approved V1/V2 records remain readable and valid.
    """
    details = data.get("visual_details")
    ensure(isinstance(details, dict), "CharacterDesignCardV2.1 needs visual_details")
    seen_descriptions = set()
    generic_only = {"结构清楚", "自然垂落", "真实质感", "精致漂亮", "干净利落",
                    "清秀好看", "自然发型", "普通体态", "无特别设计"}
    for domain, fields in DETAIL_FIELDS.items():
        section = details.get(domain)
        ensure(isinstance(section, dict), f"visual_details.{domain} must be an object")
        for field in fields:
            value = section.get(field)
            ensure(isinstance(value, str) and len(value.strip()) >= 8,
                   f"visual_details.{domain}.{field} needs a concrete visible description")
            normalized = re.sub(r"[\s，。；、,.!！:：]+", "", value)
            ensure(normalized not in seen_descriptions and normalized not in generic_only,
                   f"visual_details.{domain}.{field} repeats or uses generic wording")
            seen_descriptions.add(normalized)
    if data["schema_version"] == "CharacterDesignCardV2.5":
        return phased.validate_compiled_coverage(_runtime(), data)
    coverage = data.get("specialist_coverage")
    ensure(isinstance(coverage, dict), "CharacterDesignCardV2.1 needs specialist_coverage")
    valid_detail_paths = {f"{domain}.{field}" for domain, fields in DETAIL_FIELDS.items() for field in fields}
    domains = (SPECIALIST_DOMAINS_V24 if data["schema_version"] == "CharacterDesignCardV2.4"
               else SPECIALIST_DOMAINS_V22 if data["schema_version"] == "CharacterDesignCardV2.2"
               else SPECIALIST_DOMAINS)
    for specialist in domains:
        item = coverage.get(specialist)
        ensure(isinstance(item, dict), f"specialist_coverage.{specialist} must be an object")
        ensure(item.get("status") in {"used", "not_needed"},
               f"specialist_coverage.{specialist}.status must be used or not_needed")
        require_text(item, "decision")
        if item["status"] == "used":
            require_text(item, "proposal_ref")
            applied = item.get("applied_fields")
            ensure(isinstance(applied, list) and applied and
                   all(isinstance(path, str) and path in valid_detail_paths for path in applied),
                   f"specialist_coverage.{specialist}.applied_fields must point to visual_details")
        else:
            ensure(item.get("applied_fields") in (None, []),
                   f"specialist_coverage.{specialist} cannot apply fields when not_needed")


def validate_feature_focus(data):
    focus = data.get("feature_focus")
    ensure(isinstance(focus, dict), "V2.2 needs feature_focus")
    require_text(focus, "core_sentence")
    anchors = focus.get("primary_anchors")
    ensure(isinstance(anchors, list) and anchors, "feature_focus needs primary_anchors")
    for anchor in anchors:
        ensure(isinstance(anchor, dict), "Each primary anchor must be an object")
        for key in ("part", "geometry", "basis"):
            require_text(anchor, key)
        views = anchor.get("visible_views")
        ensure(isinstance(views, list) and views and set(views) <= VISIBLE_VIEWS,
               "Anchor visible_views must name supported views")
    if len(anchors) not in (2, 3):
        require_text(focus, "anchor_count_rationale")
    quiet = focus.get("quiet_features")
    ensure(isinstance(quiet, list), "feature_focus.quiet_features must be a list")
    for item in quiet:
        ensure(isinstance(item, dict), "Each quiet feature must be an object")
        require_text(item, "part")
        require_text(item, "decision")
    imperfection = focus.get("imperfection_policy")
    ensure(isinstance(imperfection, dict), "feature_focus needs imperfection_policy")
    ensure(imperfection.get("status") in {"none", "existing", "operator_approved"},
           "imperfection_policy.status must be none, existing or operator_approved")
    require_text(imperfection, "detail")
    require_text(imperfection, "basis")
    checks = focus.get("view_checks")
    ensure(isinstance(checks, dict), "feature_focus needs view_checks")
    for name in ("silhouette", "occlusion"):
        item = checks.get(name)
        ensure(isinstance(item, dict) and item.get("status") in {"passed", "failed", "not_tested"},
               f"view_checks.{name} needs status")
        require_text(item, "evidence")


def validate_body_form(data):
    body = data.get("body_form")
    ensure(isinstance(body, dict), "V2.2 needs body_form")
    for group, fields in {"proportions": ("torso_legs", "arm_segments", "leg_segments"),
                          "masses": ("head", "ribcage", "pelvis", "relationships"),
                          "views": ("front", "side", "back"),
                          "action_check": ("stance", "script_action", "mobility_result", "test_status")}.items():
        section = body.get(group)
        ensure(isinstance(section, dict), f"body_form.{group} must be an object")
        for field in fields:
            require_text(section, field)
    ensure(body["action_check"]["test_status"] in {"passed", "failed", "not_tested"},
           "body_form.action_check.test_status is invalid")


def validate_focus_and_form(data):
    validate_feature_focus(data)
    validate_body_form(data)


def validate_body_proportion_anchors(data):
    """Gate newly submitted V2.2 human cards; old approvals remain readable."""
    body = data.get("body_form") or {}
    anchors = body.get("proportion_anchors")
    ensure(isinstance(anchors, dict), "body_form.proportion_anchors is required for a new human card")
    require_text(anchors, "measurement_frame")
    ensure(len(anchors["measurement_frame"].strip()) >= 12,
           "proportion_anchors.measurement_frame needs a pose and measurement endpoints")
    relations = {}
    for name, point_groups in BODY_PROPORTION_POINTS.items():
        anchor = anchors.get(name)
        ensure(isinstance(anchor, dict), f"proportion_anchors.{name} must be an object")
        ensure(anchor.get("mode") in {"numeric", "landmark"},
               f"proportion_anchors.{name}.mode must be numeric or landmark")
        points = anchor.get("reference_points")
        ensure(isinstance(points, list) and len(points) >= 2 and
               all(isinstance(point, str) and point.strip() for point in points) and
               len(set(points)) == len(points),
               f"proportion_anchors.{name}.reference_points needs distinct body landmarks")
        combined = " ".join(points)
        ensure(all(any(term in combined for term in group) for group in point_groups),
               f"proportion_anchors.{name} needs the named body regions")
        require_text(anchor, "relation")
        relation = anchor["relation"].strip()
        ensure(len(relation) >= 12 and all(point in relation for point in points),
               f"proportion_anchors.{name}.relation must compare its reference points")
        if anchor["mode"] == "numeric":
            ensure(bool(re.search(r"\d+(?:\.\d+)?\s*(?:%|％|[:：]|倍|个头|头身)", relation)),
                   f"proportion_anchors.{name}.relation needs an explicit ratio")
        else:
            ensure(any(word in relation for word in ("高于", "低于", "宽于", "窄于", "齐平",
                                                  "落在", "位于", "超过", "接近", "短于", "长于")),
                   f"proportion_anchors.{name}.relation needs a definite landmark comparison")
        require_text(anchor, "basis")
        ensure(len(anchor["basis"].strip()) >= 8,
               f"proportion_anchors.{name}.basis must distinguish fact from design choice")
        relations[name] = relation
    ensure(anchors["head_body"]["mode"] == "numeric",
           "proportion_anchors.head_body needs a proposed or approved head-to-height ratio")
    details = data["visual_details"]["body"]["frame_proportions"]
    ensure(all(relations[name] in details for name in ("head_body", "shoulder_hip", "torso_legs")),
           "visual_details.body.frame_proportions must show head, shoulder/hip and torso/leg anchors")
    for name in ("torso_legs", "arm_segments", "leg_segments"):
        ensure(relations[name] in body["proportions"][name],
               f"body_form.proportions.{name} must show its concrete proportion anchor")


def validate_full_body_prompt_proportions(prompt_package, design_card):
    """Copy approved body anchors into each new full-body prompt and its checks."""
    validate_body_proportion_anchors(design_card)
    anchors = design_card["body_form"]["proportion_anchors"]
    required = ("head_body", "shoulder_hip", "torso_legs")
    for prompt in prompt_package["prompts"]:
        ensure(all(anchors[name]["relation"] in prompt["text"] for name in required),
               f"Full-body prompt {prompt['id']} must carry approved body proportion anchors")
    checks = "\n".join(prompt_package["acceptance_checks"])
    ensure(all(anchors[name]["relation"] in checks for name in ("head_body", "torso_legs")),
           "Full-body acceptance checks must verify head/body and torso/leg anchors")


def validate_model_card_attire(prompt_package, design_card):
    """Check stage attire for new human prompt submissions without changing old approvals."""
    stage = prompt_package["stage"]
    if design_card.get("morphology") not in {"human", "humanoid"} or stage not in MODEL_CARD_ATTIRE:
        return
    profile = prompt_package.get("reference_attire")
    allowed = MODEL_CARD_ATTIRE[stage]
    ensure(profile in allowed or profile == "approved_exception",
           f"{stage} human model card needs a stage-appropriate reference_attire")
    if profile == "approved_exception":
        require_text(prompt_package, "reference_attire_basis")
        require_text(prompt_package, "reference_attire_description")
        tokens = (prompt_package["reference_attire_description"],)
    else:
        tokens = allowed[profile]
    for prompt in prompt_package["prompts"]:
        ensure(all(token in prompt["text"] for token in tokens),
               f"{stage} prompt {prompt['id']} must describe model-card attire {profile}")
    checks = "\n".join(prompt_package["acceptance_checks"])
    ensure(all(token in checks for token in tokens),
           f"{stage} acceptance checks must verify model-card attire {profile}")


def validate_expression_attire_transition(prompt_package, avatar_package):
    """Expression grid inherits the avatar, except a recorded clothed fallback."""
    previous = avatar_package.get("reference_attire")
    current = prompt_package.get("reference_attire")
    if not previous or previous == current:
        return
    ensure(previous == "face_only" and current in {"white_tank", "white_sports_tank"}
           and isinstance(prompt_package.get("reference_attire_basis"), str)
           and prompt_package["reference_attire_basis"].strip(),
           "Expression model-card attire must match approved avatar or document a clothed fallback")


def checked_handoff_file(root, relative, expected_sha, label):
    ensure(isinstance(relative, str) and relative.startswith("drafts/specialists/") and
           relative.endswith(".json") and ".." not in Path(relative).parts,
           f"{label} must be a project-relative drafts/specialists JSON path")
    base = (root / "drafts" / "specialists").resolve()
    target = (root / relative).resolve()
    ensure(target.is_relative_to(base) and target.is_file(), f"{label} missing or outside project")
    ensure(isinstance(expected_sha, str) and re.fullmatch(r"[0-9a-f]{64}", expected_sha) and
           digest(target) == expected_sha, f"{label} SHA mismatch")
    return read_json(target)


def validate_design_handoffs(data, root):
    from validate_specialist_proposal import validate as validate_proposal
    route = checked_handoff_file(root, data.get("route_ref"), data.get("route_sha256"), "design route")
    ensure(route.get("schema_version") == "CharacterSpecialistRouteV1" and
           route.get("character_id") == data["character_id"] and
           route.get("variant_id") == data["variant_id"], "Design route target mismatch")
    entries = route.get("specialists")
    domains = (SPECIALIST_DOMAINS_V24 if data["schema_version"] == "CharacterDesignCardV2.4"
               else SPECIALIST_DOMAINS_V22)
    ensure(isinstance(entries, dict) and set(entries) == set(domains),
           f"Design route must cover {len(domains)} specialists")
    details = data["visual_details"]
    for specialist in domains:
        entry = entries[specialist]
        ensure(isinstance(entry, dict) and entry.get("decision") in {"invoke", "skip"},
               f"Invalid route decision: {specialist}")
        require_text(entry, "trigger")
        require_text(entry, "reason")
        coverage = data["specialist_coverage"][specialist]
        used = coverage["status"] == "used"
        ensure((entry["decision"] == "invoke") == used,
               f"Route/coverage mismatch: {specialist}")
        if not used:
            continue
        proposal = checked_handoff_file(root, coverage["proposal_ref"],
                                        coverage.get("proposal_sha256"), specialist)
        ensure(proposal.get("schema_version") == "CharacterSpecialistProposalV1.1",
               f"V2.2 handoff needs V1.1 proposal: {specialist}")
        validate_proposal(proposal)
        ensure(proposal["specialist"] == specialist and
               proposal["character_id"] == data["character_id"] and
               proposal.get("variant_id") == data["variant_id"],
               f"Proposal target mismatch: {specialist}")
        chosen = coverage.get("selected_option_id")
        option = next((x for x in proposal["options"] if x["id"] == chosen), None)
        ensure(option is not None, f"Selected option missing: {specialist}")
        mappings = coverage.get("applied_elements")
        ensure(isinstance(mappings, list) and mappings, f"Applied element trace missing: {specialist}")
        ensure({x.get("field") for x in mappings if isinstance(x, dict)} ==
               set(coverage["applied_fields"]), f"Applied field trace mismatch: {specialist}")
        for mapping in mappings:
            ensure(isinstance(mapping, dict) and isinstance(mapping.get("element_index"), int) and
                   not isinstance(mapping["element_index"], bool) and
                   0 <= mapping["element_index"] < len(option["design_elements"]),
                   f"Applied element index invalid: {specialist}")
            domain, field = mapping["field"].split(".", 1)
            ensure(domain in SPECIALIST_FIELD_DOMAINS.get(specialist, set(DETAIL_FIELDS)),
                   f"Applied field outside specialist scope: {specialist}/{mapping['field']}")
            ensure(isinstance(details[domain][field], str) and details[domain][field].strip(),
                   f"Applied field empty: {mapping['field']}")


def validate_world_and_face(data, allow_proposals=False):
    statuses = {"script_fact", "approved_choice"}
    if allow_proposals or data.get("schema_version") == "CharacterDesignCardV2.5":
        statuses |= {"inference", "creative_choice"}
    world = data.get("world_influences")
    ensure(isinstance(world, dict), "V2.4 needs world_influences")
    for key in ("environment", "technology", "resources_and_access"):
        require_text(world, key)
    effects = world.get("appearance_effects")
    ensure(isinstance(effects, list), "world_influences.appearance_effects must be a list")
    for effect in effects:
        ensure(isinstance(effect, dict), "World appearance effect must be an object")
        for key in ("feature", "mechanism", "basis", "evidence_status"):
            require_text(effect, key)
        ensure(effect["evidence_status"] in statuses,
               "World appearance effects must be script facts or approved choices")
    surface = data.get("facial_surface")
    ensure(isinstance(surface, dict), "V2.4 needs facial_surface")
    for group in ("stable_marks", "applied_decoration", "temporary_effects"):
        items = surface.get(group)
        ensure(isinstance(items, list), f"facial_surface.{group} must be a list")
        for item in items:
            ensure(isinstance(item, dict), f"facial_surface.{group} items must be objects")
            for key in ("feature", "placement", "visible_form", "narrative_basis", "continuity", "evidence_status"):
                require_text(item, key)
            ensure(item["evidence_status"] in statuses,
                   f"facial_surface.{group} must be script facts or approved choices")
    require_text(surface, "absence_or_focus_decision")


def _xlsx_rows(path):
    """Read cell values with the standard library; no Excel runtime required."""
    with zipfile.ZipFile(path) as archive:
        book = ET.fromstring(archive.read("xl/workbook.xml"))
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {item.attrib["Id"]: item.attrib["Target"] for item in rels}
        strings = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            strings = ["".join(t.text or "" for t in item.findall(".//m:t", NS))
                       for item in root.findall("m:si", NS)]
        result = {}
        for sheet in book.findall("m:sheets/m:sheet", NS):
            target = targets[sheet.attrib[f"{{{NS['r']}}}id"]].lstrip("/")
            if not target.startswith("xl/"):
                target = "xl/" + target
            xml = ET.fromstring(archive.read(target))
            rows = []
            for row in xml.findall(".//m:sheetData/m:row", NS):
                cells = {}
                for cell in row.findall("m:c", NS):
                    match = re.match(r"([A-Z]+)", cell.attrib.get("r", ""))
                    if not match:
                        continue
                    col = 0
                    for char in match.group(1):
                        col = col * 26 + ord(char) - 64
                    val = cell.find("m:v", NS)
                    if cell.attrib.get("t") == "inlineStr":
                        text = "".join(t.text or "" for t in cell.findall(".//m:t", NS))
                    elif val is None:
                        text = ""
                    elif cell.attrib.get("t") == "s":
                        text = strings[int(val.text or "0")]
                    else:
                        text = val.text or ""
                    cells[col] = text
                if cells:
                    rows.append([cells.get(i, "") for i in range(1, max(cells) + 1)])
            result[sheet.attrib["name"]] = rows
        return result


def load_source(path):
    path = Path(path).expanduser().resolve()
    ensure(path.is_file(), f"Input file missing: {path}")
    suffix = path.suffix.lower()
    ensure(suffix in SUPPORTED_INPUTS, f"Unsupported input: {path.name}")
    if suffix == ".json":
        return read_json(path)
    if suffix in {".md", ".markdown", ".txt"}:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
        return {"format": "markdown", "lines": [
            {"ref": f"{path.name}:L{i}", "text": text} for i, text in enumerate(lines, 1)]}
    sheets = _xlsx_rows(path)
    return {"format": "xlsx", "sheets": {name: [
        {"ref": f"{path.name}:{name}!R{i}", "cells": row}
        for i, row in enumerate(rows, 1)] for name, rows in sheets.items()}}


def _characters_from_markdown(data):
    lines = [row["text"] for row in data["lines"]]
    result = []
    headers = None
    for line in lines:
        if not line.lstrip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if "资产ID" in cells and ("人物名" in cells or "角色名" in cells):
            headers = cells
            continue
        if headers and re.fullmatch(r"\s*:?-+:?\s*", cells[0]):
            continue
        if headers and len(cells) >= len(headers):
            row = dict(zip(headers, cells))
            ident = row.get("资产ID", "")
            if ident.startswith("CHR-"):
                result.append({"id": ident, "name": row.get("人物名") or row.get("角色名"),
                               "tier": row.get("角色层级", "未分层"),
                               "script_facts": [row.get("剧本明确特征", "")],
                               "source_refs": [row.get("来源位置", "")],
                               "states": [{"id": row.get("状态ID", "S01"),
                                           "name": row.get("状态名", "常态")} ]})
    return result


def roster_from_assets(data):
    if isinstance(data, dict) and isinstance(data.get("characters"), list):
        source = data["characters"]
    elif isinstance(data, dict) and data.get("format") == "xlsx":
        rows = data["sheets"].get("人物", [])
        ensure(rows, "Asset workbook has no 人物 sheet")
        headers = rows[0]["cells"]
        source = []
        for row in rows[1:]:
            fields = dict(zip(headers, row["cells"]))
            ident = str(fields.get("资产ID", ""))
            if ident.startswith("CHR-"):
                source.append({"id": ident, "name": fields.get("人物名", ""),
                               "tier": fields.get("角色层级", "未分层"),
                               "script_facts": [fields.get("剧本明确特征", "")],
                               "source_refs": [fields.get("来源位置", "")],
                               "states": [{"id": fields.get("状态ID", "S01"),
                                           "name": fields.get("状态名", "常态"),
                                           "script_facts": [fields.get("状态明确特征", "")] }]})
    elif isinstance(data, dict) and data.get("format") == "markdown":
        source = _characters_from_markdown(data)
    else:
        raise ValueError("Asset table has no readable character roster")
    ensure(source, "Asset table contains no characters")
    combined = {}
    for item in source:
        ident = safe_id(str(item.get("id", "")))
        ensure(str(item.get("name", "")).strip(), f"Character {ident} has no name")
        if ident not in combined:
            combined[ident] = copy.deepcopy(item)
            combined[ident]["states"] = list(item.get("states") or [])
        else:
            combined[ident]["states"].extend(item.get("states") or [])
    return [{"id": ident, "name": item["name"], "tier": item.get("tier", "未分层"),
             "priority": "deep" if item.get("tier") in HEAVY_TIERS else "light",
             "states": item.get("states", []), "aliases": item.get("aliases", []),
             "asset_digest": digest(item)} for ident, item in combined.items()]


def validate_lineage(screenplay_path, screenplay, assets, scene_log=None):
    if isinstance(screenplay, dict) and screenplay.get("format") not in {"markdown", "xlsx"}:
        ensure(isinstance(screenplay.get("episodes"), list),
               "Standardized screenplay JSON needs an episodes array")
    if isinstance(assets, dict) and isinstance(assets.get("source"), dict):
        source_hash = assets["source"].get("sha256")
        if source_hash:
            ensure(source_hash == digest(Path(screenplay_path).expanduser().resolve()),
                   "Asset table was derived from a different screenplay version")
    if isinstance(screenplay, dict) and isinstance(scene_log, dict):
        original = screenplay.get("source_manifest", {}).get("source_sha256")
        scene_original = scene_log.get("source_manifest", {}).get("source_sha256")
        if original and scene_original:
            ensure(original == scene_original,
                   "Scene log was derived from a different screenplay source")


def _copy_input(root, kind, path, revision):
    source = Path(path).expanduser().resolve()
    loaded = load_source(source)
    target = root / "inputs" / f"rev-{revision:03d}" / f"{kind}{source.suffix.lower()}"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return {"path": str(target.relative_to(root)), "original_name": source.name,
            "format": source.suffix.lower().lstrip("."), "sha256": digest(target)}, loaded


def _record_key(kind, character_id=None, variant_id=None, stage=None):
    if kind in {"visual-bible", "cast-plan"}:
        return kind
    safe_id(character_id)
    safe_id(variant_id or "base")
    if kind in {"ensemble-design", "extra-design"}:
        return ensemble.key(character_id, variant_id or "base") if kind == "ensemble-design" else ensemble.extra_key(character_id, variant_id or "base")
    if kind == "design-card":
        return f"design-card:{character_id}:{variant_id or 'base'}"
    ensure(kind == "prompt-package" and stage in STAGES, "Invalid record kind or stage")
    return f"prompt-package:{stage}:{character_id}:{variant_id or 'base'}"


def _require_approved(state, key):
    value = state["records"].get(key)
    ensure(value and value.get("approval") and not value.get("stale"),
           f"Required approved record missing or stale: {key}")
    return value


def _checked_record(root, state, key):
    value = _require_approved(state, key)
    ensure(digest(read_json(root / value["path"])) == value["sha256"],
           f"Approved record contents changed: {key}")
    ensure(value["approval"].get("sha256") == value["sha256"],
           f"Approval refers to another record version: {key}")
    if key.startswith("design-card:"):
        card = read_json(root / value["path"])
        if card.get("schema_version") in {"CharacterDesignCardV2.2", "CharacterDesignCardV2.4"} and card.get("morphology") in {"human", "humanoid"}:
            validate_design_handoffs(card, root)
    if phased.enabled(state):
        phased.checked_dependencies(_runtime(), root, state, key, read_json(root / value["path"]))
        if key.startswith(("ensemble-design:", "extra-design:")):
            check = ensemble.validate_extra if key.startswith("extra-design:") else ensemble.validate
            check(_runtime(), root, state, read_json(root / value["path"]),
                  key.split(":")[1], key.split(":")[2])
    return value


def _checked_image(root, state, stage, character_id, variant_id):
    image = _approved_image(state, stage, character_id, variant_id)
    ensure(digest(root / image["path"]) == image["sha256"],
           f"Approved image contents changed: {image['id']}")
    review = state["reviews"].get(image["id"])
    ensure(review and digest(read_json(root / review["path"])) == review["sha256"],
           f"Review missing or changed: {image['id']}")
    ensure(image["approval"].get("review_sha256") == review["sha256"],
           f"Image approval refers to another review: {image['id']}")
    ensure(image["approval"].get("image_sha256") == image["sha256"],
           f"Image approval refers to another image version: {image['id']}")
    ensure(read_json(root / review["path"]).get("verdict") == "pass",
           f"Approved image review does not pass: {image['id']}")
    prompt = _checked_record(root, state, _record_key(
        "prompt-package", character_id, variant_id, stage))
    ensure(image["prompt_sha256"] == prompt["sha256"],
           f"Image was generated from another prompt version: {image['id']}")
    if phased.enabled(state) and image.get("migration_legacy_identity"):
        legacy = image["migration_legacy_identity"]
        card = _checked_record(root, state, legacy["card_key"])
        package = read_json(root / prompt["path"])
        ensure(card["sha256"] == legacy["card_sha256"] == package.get("design_card_sha256"),
               "Migrated identity image lost its historical approved card")
        ensure(image.get("purpose", "production") == "production", "Preview candidates cannot be migrated identity anchors")
    elif phased.enabled(state):
        package = read_json(root / prompt["path"])
        if ensemble.mode(_runtime(), root, state, character_id) in {"ensemble", "speaking_extra"}:
            ensemble.resolve(_runtime(), root, state, package, character_id, variant_id)
        else:
            phased.resolve_basis(_runtime(), root, state, package, character_id, variant_id, stage, force_approved=True)
        ensure(image.get("purpose", "production") == "production", "Preview candidates cannot be downstream anchors")
    return image


def _approved_image(state, stage, character_id, variant_id):
    matching = [image for image in state["images"] if image["stage"] == stage
                and image["character_id"] == character_id
                and image["variant_id"] == variant_id and image.get("approval")
                and not image.get("stale")]
    ensure(len(matching) == 1, f"One approved {stage} image required for {character_id}/{variant_id}")
    return matching[0]


def _invalidate(state, character_id=None, variant_id=None, start="visual-bible"):
    downstream = {
        "visual-bible": {"visual-bible", "cast-plan", "design-card", "ensemble-design", "extra-design", *STAGES},
        "cast-plan": {"cast-plan", "design-card", "ensemble-design", "extra-design", *STAGES},
        "design-card": {"design-card", "ensemble-design", "extra-design", *STAGES},
        "ensemble-design": {"ensemble-design", "execution"},
        "extra-design": {"extra-design", "execution"},
        "avatar": set(STAGES),
        "expression": {"expression", "full_body", "costume_design", "execution"},
        "full_body": {"full_body", "costume_design", "execution"},
        "costume_design": {"costume_design", "execution"},
        "execution": {"execution"},
    }
    affected = downstream[start]
    if phased.enabled(state) and start in {"visual-bible", "cast-plan", "design-card"}:
        for key, value in state["records"].items():
            if key.startswith(("design-brief:", "stage-design:", "costume-bible:")) and (not character_id or character_id in key.split(":")):
                value.update(stale=True, approval=None)
    for key, value in state["records"].items():
        parts = key.split(":")
        if character_id and (len(parts) < 2 or character_id not in parts):
            continue
        if variant_id and len(parts) > 2 and parts[-1] != variant_id:
            continue
        level = parts[1] if parts[0] == "prompt-package" else parts[0]
        if level in affected:
            value["stale"] = True
            value["approval"] = None
    for image in state["images"]:
        if character_id and image["character_id"] != character_id:
            continue
        if variant_id and image["variant_id"] != variant_id:
            continue
        if image["stage"] in affected:
            image["stale"] = True
            image["approval"] = None


def _validate_record(kind, data, state, character_id=None, variant_id=None, stage=None):
    ensure(isinstance(data, dict), "Record must be a JSON object")
    expected = {"visual-bible": "ProjectVisualBibleV1", "cast-plan": "CastPlanV1",
                "design-card": "CharacterDesignCardV1",
                "prompt-package": "CharacterPromptPackageV1"}[kind]
    accepted = {"cast-plan": {"CastPlanV1", "CastPlanV2"},
                "design-card": {"CharacterDesignCardV1", "CharacterDesignCardV2",
                "CharacterDesignCardV2.1", "CharacterDesignCardV2.2", "CharacterDesignCardV2.4", "CharacterDesignCardV2.5"}}
    ensure(data.get("schema_version") in accepted.get(kind, {expected}),
           f"Expected one of {sorted(accepted.get(kind, {expected}))}")
    require_list(data, "unresolved") if kind != "prompt-package" else None
    if kind == "visual-bible":
        require_text(data, "project_id")
        ensure(data["project_id"] == state["project_id"], "Wrong project_id")
        require_list(data, "world_rules")
        ensure(isinstance(data.get("style"), dict), "style must be an object")
        require_list(data, "evidence")
        for fact in data["evidence"]:
            require_text(fact, "claim")
            require_list(fact, "source_refs")
            ensure(fact["source_refs"], "World evidence needs source_refs")
    elif kind == "cast-plan":
        require_list(data, "characters")
        expected_ids = {row["id"] for row in state["roster"]}
        actual = {row.get("id") for row in data["characters"]}
        ensure(actual == expected_ids, "Cast plan must cover the asset-table roster exactly")
        for item in data["characters"]:
            require_text(item, "design_distinction")
            if data["schema_version"] == "CastPlanV2":
                axes = item.get("recognition_axes")
                ensure(isinstance(axes, dict), "CastPlanV2 rows need recognition_axes")
                for axis in RECOGNITION_AXES:
                    require_text(axes, axis)
    elif kind == "design-card":
        ensure(data.get("character_id") == character_id, "Wrong character_id")
        ensure(data.get("variant_id") == variant_id, "Wrong variant_id")
        ensure(data.get("morphology") in {"human", "humanoid", "nonhuman"},
               "morphology must be human, humanoid or nonhuman")
        for field in ("facts", "inferences", "approved_choices", "identity_invariants"):
            require_list(data, field)
        ensure(isinstance(data.get("appearance"), dict), "appearance must be an object")
        ensure(isinstance(data.get("costume"), dict), "costume must be an object")
        for fact in data["facts"]:
            require_text(fact, "text")
            require_list(fact, "source_refs")
            ensure(fact["source_refs"], "A script fact needs source_refs")
        for idea in data["inferences"]:
            require_text(idea, "text")
            require_list(idea, "basis_refs")
        for choice in data["approved_choices"]:
            require_text(choice, "field")
            require_text(choice, "value")
            require_text(choice, "rationale")
        if data["schema_version"] in {"CharacterDesignCardV2", "CharacterDesignCardV2.1", "CharacterDesignCardV2.2", "CharacterDesignCardV2.4", "CharacterDesignCardV2.5"}:
            axes = data.get("recognition_axes")
            ensure(isinstance(axes, dict), "CharacterDesignCardV2 needs recognition_axes")
            for axis in RECOGNITION_AXES:
                require_text(axes, axis)
            review = data.get("differentiation_review")
            ensure(isinstance(review, dict), "CharacterDesignCardV2 needs differentiation_review")
            require_list(review, "closest_character_ids")
            require_list(review, "shared_features")
            require_list(review, "distinct_features")
            require_text(review, "realism_check")
            if review["closest_character_ids"]:
                ensure(review["distinct_features"],
                       "Describe visible differences from the closest cast members")
        if data["schema_version"] in {"CharacterDesignCardV2.1", "CharacterDesignCardV2.2", "CharacterDesignCardV2.4", "CharacterDesignCardV2.5"} and data["morphology"] in {"human", "humanoid"}:
            validate_visual_details(data)
        if data["schema_version"] in {"CharacterDesignCardV2.2", "CharacterDesignCardV2.4", "CharacterDesignCardV2.5"} and data["morphology"] in {"human", "humanoid"}:
            validate_focus_and_form(data)
        if data["schema_version"] in {"CharacterDesignCardV2.4", "CharacterDesignCardV2.5"}:
            validate_world_and_face(data)
    else:
        ensure(data.get("character_id") == character_id and data.get("variant_id") == variant_id,
               "Prompt target does not match character/variant")
        ensure(data.get("stage") == stage, "Prompt stage mismatch")
        ensure(str(data.get("target_model", "")).startswith("gpt-image-2.5"),
               "Prompts must target GPT Image 2.5")
        require_list(data, "reference_images")
        require_list(data, "prompts")
        require_list(data, "acceptance_checks")
        if phased.enabled(state):
            ensure(isinstance(data.get("design_basis"), dict), "Phased prompts need design_basis")
        else:
            require_text(data, "design_card_sha256")
        ensure(isinstance(data.get("anchor_images"), dict),
               "anchor_images must be a stage-to-SHA object")
        ensure(data["prompts"], "Prompt package is empty")
        ensure(data["acceptance_checks"], "Prompt package needs acceptance checks")
        prompt_ids = []
        for prompt in data["prompts"]:
            require_text(prompt, "id")
            require_text(prompt, "text")
            prompt_ids.append(prompt["id"])
        ensure(len(set(prompt_ids)) == len(prompt_ids), "Prompt IDs must be unique")
        if stage in {"avatar", "full_body"}:
            if stage == "avatar":
                minimum = 1 if phased.enabled(state) else 2
                ensure(minimum <= len(data["prompts"]) <= 3, "Avatar needs one recommended candidate or up to three alternatives")
            default_ratio = "3:4" if stage == "avatar" else "9:16"
            stage_label = "Avatar" if stage == "avatar" else "Full-body"
            ratio = data.get("aspect_ratio")
            ensure(isinstance(ratio, str) and re.fullmatch(r"[1-9][0-9]*:[1-9][0-9]*", ratio),
                   f"{stage_label} prompt package needs aspect_ratio; default is {default_ratio}")
            if ratio != default_ratio:
                require_text(data, "aspect_ratio_basis")
                ensure(data.get("aspect_ratio_explicit_user_override") is True,
                       f"{stage_label} ratio may differ from {default_ratio} only by explicit user override")
            for prompt in data["prompts"]:
                ensure(ratio in prompt["text"],
                       f"{stage_label} prompt {prompt['id']} must state canvas ratio {ratio}")
            if stage == "full_body":
                ensure(any(ratio in check for check in data["acceptance_checks"]),
                       "Full-body acceptance checks must verify canvas ratio")
        if stage == "expression":
            require_list(data, "labels")
            ensure(len(data["labels"]) in {9, 16}, "Expression sheet needs 9 or 16 Chinese labels")
            if state.get("pipeline_version", 1) >= 2 and len(data["labels"]) != 9:
                ensure(data.get("grid_explicit_user_override") is True and
                       isinstance(data.get("grid_override_basis"), str) and
                       data["grid_override_basis"].strip(),
                       "V0.2.4.1 expression stage defaults to nine-grid; sixteen needs explicit user choice")
            ensure(all(isinstance(x, str) and x.strip() for x in data["labels"]),
                   "Expression labels cannot be empty")
            ensure(all(re.search(r"[\u3400-\u9fff]", x) for x in data["labels"]),
                   "Each expression label must contain Chinese text")
        if stage == "full_body":
            ensure(data.get("head_visible") is True, "Standalone full-body image includes head")
            ensure(data.get("feet_visible") is True, "Standalone full-body image includes feet")
        if stage == "costume_design":
            ensure(state.get("pipeline_version", 1) >= 2, "Costume design stage is only in V0.2.4.1 projects")
            require_text(data, "variant_name")
            ensure(data["variant_name"] == variant_name(state, character_id, variant_id),
                   "Costume design must name its exact asset-table variant")
            ensure(any("服饰" in x or "服装" in x for x in data["acceptance_checks"]),
                   "Costume design checks must cover visible garment structure")
        if stage == "execution" and state.get("pipeline_version", 1) >= 3 and data.get("morphology") != "group":
            ratio = data.get("aspect_ratio")
            ensure(isinstance(ratio, str) and re.fullmatch(r"[1-9][0-9]*:[1-9][0-9]*", ratio),
                   "V3 costume execution sheet needs aspect_ratio; default is 9:16")
            if ratio != "9:16":
                require_text(data, "aspect_ratio_basis")
                ensure(data.get("aspect_ratio_explicit_user_override") is True,
                       "V3 costume execution ratio may differ from 9:16 only by explicit user override")
            ensure(all(ratio in prompt["text"] for prompt in data["prompts"]),
                   "Each costume execution prompt must state its canvas ratio")
            ensure(any(ratio in check for check in data["acceptance_checks"]),
                   "Costume execution review must verify the canvas ratio")
            ensure(any("服饰" in check or "服装" in check for check in data["acceptance_checks"]),
                   "Costume execution review must check garment structure")
            require_text(data, "variant_name")
            ensure(data["variant_name"] == variant_name(state, character_id, variant_id),
                   "Costume execution must use the asset-table state name")
        if stage == "execution" and data.get("morphology") == "human":
            layout = data.get("layout") or {}
            ensure(layout.get("top_left") == "front_face" and
                   layout.get("top_right") == "three_quarter_face_45" and
                   layout.get("bottom_left") == "headless_enlarged_front_costume" and
                   layout.get("bottom_right") == "complete_back_head_to_shoes",
                   "Human execution sheet must use the approved four-panel layout")


@contextlib.contextmanager
def locked_project(root):
    import fcntl
    root = Path(root).expanduser().resolve()
    ensure((root / "project.json").is_file(), f"Not a character project: {root}")
    with (root / ".lock").open("a+") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        state = read_json(root / "project.json")
        ensure(state.get("schema_version") == SCHEMA, "Unsupported project state")
        yield root, state
        state["revision"] += 1
        write_json(root / "project.json", state)


def cmd_init(args):
    root = Path(args.project_root).expanduser().resolve()
    ensure(not root.exists(), f"Project directory already exists: {root}")
    snapshot = None
    if args.snapshot:
        snapshot_path = Path(args.snapshot).expanduser().resolve()
        snapshot = read_json(snapshot_path)
        ensure(snapshot.get("schema_version") == "AssetProjectSnapshotV1",
               "Expected AssetProjectSnapshotV1")
        ensure(isinstance(snapshot.get("sources"), dict), "Snapshot sources missing")
        if args.project_id:
            ensure(args.project_id == snapshot.get("project_id"), "Snapshot project_id mismatch")
        args.project_id = snapshot.get("project_id")
        for kind in ("screenplay", "asset_table", "scene_log"):
            item = snapshot["sources"].get(kind)
            if item:
                source = (snapshot_path.parent / item["path"]).resolve()
                ensure(source.is_file() and digest(source) == item.get("sha256"),
                       f"Snapshot source hash mismatch: {kind}")
                setattr(args, kind, str(source))
        bible = snapshot.get("visual_bible")
        if bible:
            bible_path = (snapshot_path.parent / bible["path"]).resolve()
            ensure(bible_path.is_file() and digest(bible_path) == bible.get("sha256"),
                   "Snapshot visual_bible hash mismatch")
            ensure(isinstance(bible.get("approval"), dict) and
                   bible["approval"].get("operator"), "Snapshot visual_bible is not approved")
    ensure(args.project_id and args.screenplay and args.asset_table,
           "project_id, screenplay and asset_table are required unless supplied by snapshot")
    safe_id(args.project_id)
    # Check the required inputs before creating the project directory.
    checked_screenplay = load_source(args.screenplay)
    checked_assets = load_source(args.asset_table)
    roster_from_assets(checked_assets)
    checked_scene_log = load_source(args.scene_log) if args.scene_log else None
    validate_lineage(args.screenplay, checked_screenplay, checked_assets, checked_scene_log)
    root.mkdir(parents=True)
    inputs, data = {}, {}
    for kind, path in (("screenplay", args.screenplay), ("asset_table", args.asset_table),
                       ("scene_log", args.scene_log)):
        if path:
            inputs[kind], data[kind] = _copy_input(root, kind, path, 1)
    roster = roster_from_assets(data["asset_table"])
    for kind, value in data.items():
        if not (isinstance(value, dict) and kind == "asset_table" and "characters" in value):
            write_json(root / "inputs" / f"rev-001/{kind}.normalized.json", value)
    progression = getattr(args, "design_progression", "phased")
    state = {"schema_version": SCHEMA, "pipeline_version": 3 if progression == "phased" else 2,
             "design_progression": progression,
             "project_id": args.project_id, "created_at": now(),
             "revision": 1, "inputs": inputs, "roster": roster, "records": {},
             "images": [], "reviews": {}, "references": [], "pending_impact": None,
             "decisions": []}
    if snapshot and snapshot.get("visual_bible"):
        bible = snapshot["visual_bible"]
        bible_path = (Path(args.snapshot).expanduser().resolve().parent / bible["path"]).resolve()
        content = read_json(bible_path)
        _validate_record("visual-bible", content, state)
        ensure(not content["unresolved"], "Approved snapshot bible has unresolved items")
        ensure(bible["approval"].get("sha256") == digest(content),
               "Snapshot approval refers to another visual_bible version")
        target = root / "records" / "visual-bible" / f"{digest(content)[:12]}.json"
        write_json(target, content)
        state["records"]["visual-bible"] = {
            "path": str(target.relative_to(root)), "sha256": digest(content),
            "submitted_at": now(), "approval": bible["approval"], "stale": False}
    write_json(root / "project.json", state)
    return {"project_root": str(root), "characters": len(roster),
            "design_progression": state["design_progression"],
            "pipeline_version": state["pipeline_version"],
            "deep_design": [row["id"] for row in roster if row["priority"] == "deep"],
            "scene_log_present": bool(args.scene_log)}


def cmd_status(args):
    root = Path(args.project_root).expanduser().resolve()
    state = read_json(root / "project.json")
    return {"project_id": state["project_id"], "revision": state["revision"],
            "design_progression": state.get("design_progression", "complete"),
            "pipeline_version": state.get("pipeline_version", 1),
            "inputs": state["inputs"], "roster": state["roster"],
            "records": {key: {"approved": bool(v.get("approval")), "stale": v.get("stale", False)}
                        for key, v in state["records"].items()},
            "images": [{key: image.get(key) for key in
                        ("id", "stage", "character_id", "variant_id", "approval", "stale")}
                       for image in state["images"]],
            "pending_impact": state["pending_impact"]}


def cmd_upgrade_pipeline(args):
    """Explicit V2→V3 migration; preserve approved identity pictures and history."""
    with locked_project(args.project_root) as (root, state):
        ensure(state.get("pipeline_version", 1) == 2,
               "Only pipeline 2 projects can use this migration")
        ensure(not state.get("pending_impact"), "Resolve source impact before migration")
        approved_garments = [x["id"] for x in state["images"] if x["stage"] in {"costume_design", "execution"}
                             and x.get("approval") and not x.get("stale")]
        ensure(not approved_garments, f"Approved garment images require the original pipeline: {approved_garments}")
        require_text({"operator": args.operator}, "operator")
        was_phased = phased.enabled(state)
        preserved_images = [x for x in state["images"] if x["stage"] in IDENTITY_STAGES
                            and x.get("approval") and not x.get("stale")]
        for image in preserved_images:
            _checked_image(root, state, image["stage"], image["character_id"], image["variant_id"])
            if not was_phased:
                prompt_key = _record_key("prompt-package", image["character_id"], image["variant_id"], image["stage"])
                package = read_json(root / state["records"][prompt_key]["path"])
                card_key = _record_key("design-card", image["character_id"], image["variant_id"])
                card = _checked_record(root, state, card_key)
                ensure(package.get("design_card_sha256") == card["sha256"], "Historical identity basis changed")
                migration_key = f"migration-design-card:{image['character_id']}:{image['variant_id']}"
                state["records"][migration_key] = copy.deepcopy(card)
                image["migration_legacy_identity"] = {"card_key": migration_key,
                                                       "card_sha256": card["sha256"]}
        preserved = [x["id"] for x in preserved_images]
        for record_key, record in state["records"].items():
            if record_key.startswith(("stage-design:costume:", "design-card:", "prompt-package:costume_design:",
                                      "prompt-package:execution:")):
                record.update(stale=True, approval=None)
        for image in state["images"]:
            if image["stage"] in {"costume_design", "execution"}:
                image.update(stale=True, approval=None)
        state["pipeline_version"] = 3
        state["design_progression"] = "phased"
        state["decisions"].append({"kind": "upgrade-pipeline", "from": 2, "to": 3,
                                   "operator": args.operator, "at": now(), "preserved_image_ids": preserved,
                                   "from_design_progression": "phased" if was_phased else "complete"})
        return {"pipeline_version": 3, "preserved_approved_identity_images": preserved,
                "requires": (["CostumeStyleBibleV1", "new state costume snapshots", "execution 9:16"]
                             if was_phased else ["ScriptContextV1", "DesignDirectionBriefV1", "approved identity/body backfill",
                                                 "CostumeStyleBibleV1", "new state costume snapshots", "execution 9:16"])}


def cmd_plan(args):
    """Read-only single or batch queue; each image remains separately reviewed and approved."""
    root = Path(args.project_root).expanduser().resolve()
    state = read_json(root / "project.json")
    ensure(not args.stage or args.stage in pipeline_stages(state),
           "Requested stage is not available in this project pipeline")
    modern = state.get("pipeline_version", 1) >= 2
    requested = ([args.character_id] if isinstance(args.character_id, str)
                 else list(args.character_id or []))
    ensure(len(requested) == len(set(requested)), "Duplicate character IDs in plan request")
    roster = [x for x in state["roster"] if not requested or x["id"] in requested]
    ensure(roster, "No matching character in roster")
    ensure(len(roster) == len(requested) if requested else True,
           "Some requested character IDs are absent")
    if args.variant_id:
        ensure(any(args.variant_id == "base" or
                   any(v.get("id") == args.variant_id for v in row.get("states", []))
                   for row in roster), "Requested variant is absent from selected roster")
    tasks = []
    for person in roster:
        asset_mode = ensemble.mode(_runtime(), root, state, person["id"])
        variants = [x["id"] for x in person.get("states", []) if x.get("id")]
        variants = variants or ["base"]
        targets = ([("execution", variant) for variant in variants] if asset_mode in {"ensemble", "speaking_extra"} else
                   [(stage, "base") for stage in IDENTITY_STAGES] +
                   [(stage, variant) for variant in variants
                    for stage in pipeline_stages(state) if stage not in IDENTITY_STAGES]
                   if modern else [(stage, variant) for variant in variants for stage in LEGACY_STAGES])
        for stage, variant in targets:
            if args.stage and stage != args.stage:
                continue
            if args.variant_id and variant != args.variant_id and stage not in IDENTITY_STAGES:
                continue
            blockers = []
            if state.get("pending_impact"):
                blockers.append("Unresolved upstream impact")
            card_variant = variant
            design_dependencies = (["script-context", ensemble.design_key(asset_mode, person["id"], variant)]
                                   if asset_mode in {"ensemble", "speaking_extra"} else
                                   phased.basis_keys(person["id"], variant, stage, state) if phased.enabled(state)
                                   else [_record_key("design-card", person["id"], card_variant)])
            for key in ("visual-bible", "cast-plan", *design_dependencies):
                try:
                    _checked_record(root, state, key)
                except (ValueError, KeyError) as exc:
                    blockers.append(str(exc))
            predecessors = () if asset_mode in {"ensemble", "speaking_extra"} else image_predecessors(state, stage)
            for prior in predecessors:
                anchor_variant = "base" if modern and prior in IDENTITY_STAGES else variant
                try:
                    _checked_image(root, state, prior, person["id"], anchor_variant)
                except (ValueError, KeyError) as exc:
                    blockers.append(str(exc))
            try:
                _checked_image(root, state, stage, person["id"], variant)
                status = "blocked" if blockers else "approved"
            except (ValueError, KeyError):
                status = "blocked" if blockers else "ready"
            task = {"asset_name": person["name"], "asset_mode": asset_mode,
                          "character_id": person["id"],
                          "variant_id": variant, "variant_name": variant_name(state, person["id"], variant),
                           "stage": stage, "status": status, "blockers": blockers}
            if phased.enabled(state) and stage == "avatar":
                task["preview_modes"] = {}
                for mode in ("direction_first", "image_first"):
                    try:
                        candidate = {"purpose": "preview", "preview_mode": mode, "design_basis": {"records": {
                            k: phased.draft(_runtime(), root, state, k)["sha256"] for k in design_dependencies}}}
                        phased.resolve_basis(_runtime(), root, state, candidate, person["id"], variant, stage)
                        task["preview_modes"][mode] = {"status": "ready"}
                    except (ValueError, KeyError) as exc:
                        task["preview_modes"][mode] = {"status": "blocked", "reason": str(exc)}
            tasks.append(task)
    return {"mode": "single" if len(requested) == 1 else "batch",
            "design_progression": state.get("design_progression", "complete"),
            "pipeline_version": state.get("pipeline_version", 1),
            "tasks": tasks}


def cmd_submit(args):
    with locked_project(args.project_root) as (root, state):
        ensure(not state["pending_impact"], "Resolve upstream impact before new design decisions")
        if args.kind in {"ensemble-design", "extra-design"}:
            return ensemble.submit(_runtime(), args, root, state)
        if args.kind in phased.KINDS:
            return phased.submit(_runtime(), args, root, state)
        ensure(not (phased.enabled(state) and args.kind == "design-card"),
               "Phased cards are mechanically composed with compile-design-card")
        content = read_json(args.file)
        character_id = args.character_id
        variant_id = args.variant_id or "base"
        modern = state.get("pipeline_version", 1) >= 2
        if args.kind in {"design-card", "prompt-package"}:
            if modern:
                require_known_variant(state, character_id, variant_id)
        asset_mode = (ensemble.mode(_runtime(), root, state, character_id)
                      if character_id and modern else "individual")
        if args.kind == "prompt-package":
            ensure(args.stage in pipeline_stages(state), "Stage is not available in this project pipeline")
            if asset_mode in {"ensemble", "speaking_extra"}:
                ensure(args.stage == "execution", "Extras have one execution sheet, not multi-stage identity images")
            if modern and args.stage in IDENTITY_STAGES:
                ensure(variant_id == "base", "V0.2.4.1 identity stages belong to the base character, not each costume variant")
        key = _record_key(args.kind, character_id, variant_id, args.stage)
        if character_id:
            ensure(character_id in {row["id"] for row in state["roster"]},
                   "Unknown character ID")
        dependencies = {"cast-plan": ["visual-bible"],
                        "design-card": ["visual-bible", "cast-plan"]}
        for dep in dependencies.get(args.kind, []):
            _checked_record(root, state, dep)
        if args.kind == "prompt-package":
            card_key = _record_key("design-card", character_id, variant_id)
            if asset_mode in {"ensemble", "speaking_extra"}:
                card = ensemble.resolve(_runtime(), root, state, content, character_id, variant_id)
                card_record = None
            elif phased.enabled(state):
                card = phased.resolve_basis(_runtime(), root, state, content, character_id, variant_id, args.stage)
                card_record = None
            else:
                card_record = _checked_record(root, state, card_key)
            anchors = {}
            if asset_mode in {"ensemble", "speaking_extra"}:
                predecessors = ()
            elif modern:
                predecessors = image_predecessors(state, args.stage)
                for anchor_stage in predecessors:
                    anchor_variant = "base" if anchor_stage in IDENTITY_STAGES else variant_id
                    anchors[anchor_stage] = _checked_image(
                        root, state, anchor_stage, character_id, anchor_variant)["sha256"]
            else:
                if args.stage in {"expression", "full_body", "execution"}:
                    anchors["avatar"] = _checked_image(root, state, "avatar", character_id, variant_id)["sha256"]
                if args.stage == "execution":
                    for anchor_stage in ("expression", "full_body"):
                        anchors[anchor_stage] = _checked_image(
                            root, state, anchor_stage, character_id, variant_id)["sha256"]
        if args.kind == "design-card" and content.get("morphology") in {"human", "humanoid"}:
            roster_item = next((row for row in state["roster"] if row["id"] == character_id), {})
            if roster_item.get("tier") in HEAVY_TIERS or roster_item.get("priority") == "deep":
                required_schema = "CharacterDesignCardV2.4" if modern else "CharacterDesignCardV2.2"
                ensure(content.get("schema_version") == required_schema,
                       f"Submitted lead/important human design cards require {required_schema}; existing approvals remain readable")
        _validate_record(args.kind, content, state, character_id, variant_id, args.stage)
        if args.kind == "design-card" and content.get("schema_version") in {"CharacterDesignCardV2.2", "CharacterDesignCardV2.4"} and content.get("morphology") in {"human", "humanoid"}:
            validate_body_proportion_anchors(content)
            validate_design_handoffs(content, root)
        if args.kind == "prompt-package":
            if not phased.enabled(state):
                ensure(content["design_card_sha256"] == card_record["sha256"],
                       "Prompt package refers to a different design card version")
            ensure(content["anchor_images"] == anchors,
                   "Prompt package anchor image versions do not match the current approvals")
            if asset_mode in {"ensemble", "speaking_extra"}:
                (ensemble.validate_extra_prompt if asset_mode == "speaking_extra" else ensemble.validate_prompt)(_runtime(), content, card)
            elif not phased.enabled(state):
                card = read_json(root / state["records"][
                    _record_key("design-card", character_id, variant_id)]["path"])
            if asset_mode not in {"ensemble", "speaking_extra"}:
                validate_model_card_attire(content, card)
            if asset_mode == "individual" and args.stage == "expression" and card.get("morphology") in {"human", "humanoid"}:
                avatar_record = state["records"][_record_key(
                    "prompt-package", character_id, "base" if modern else variant_id, "avatar")]
                validate_expression_attire_transition(
                    content, read_json(root / avatar_record["path"]))
            if asset_mode == "individual" and args.stage == "full_body" and (phased.enabled(state) or card.get("schema_version") in {"CharacterDesignCardV2.2", "CharacterDesignCardV2.4"}) and card.get("morphology") in {"human", "humanoid"}:
                validate_full_body_prompt_proportions(content, card)
            if asset_mode == "individual" and args.stage == "execution":
                if phased.enabled(state) and state.get("pipeline_version", 1) >= 3:
                    phased.validate_scene_prompt_coverage(_runtime(), root, state, content, character_id, variant_id)
                ensure(content.get("morphology") == card["morphology"],
                       "Execution prompt morphology must match the approved design card")
                if card["morphology"] != "human":
                    ensure(isinstance(card.get("execution_layout"), dict) and
                           card["execution_layout"],
                           "Nonhuman design card needs an approved execution_layout")
                    ensure(content.get("layout") == card["execution_layout"],
                           "Execution layout must match the approved design card")
        incoming = digest(content)
        prior = state["records"].get(key)
        if prior and prior["sha256"] == incoming and not prior.get("stale"):
            return {"key": key, "status": "unchanged", "sha256": incoming}
        if prior:
            level = args.stage if args.kind == "prompt-package" else args.kind
            scope_variant = (None if modern and variant_id == "base" and
                             (args.kind == "design-card" or
                              args.kind == "prompt-package" and args.stage in IDENTITY_STAGES)
                             else variant_id if character_id else None)
            _invalidate(state, character_id, scope_variant, level)
        path = root / "records" / key.replace(":", "/") / f"{incoming[:12]}.json"
        write_json(path, content)
        state["records"][key] = {"path": str(path.relative_to(root)), "sha256": incoming,
                                 "submitted_at": now(), "approval": None, "stale": False}
        if args.kind == "prompt-package":
            state["records"][key]["approval"] = {"operator": "system:contract-check",
                                                    "at": now(), "sha256": incoming}
        return {"key": key, "sha256": incoming,
                "status": "ready" if args.kind == "prompt-package" else "awaiting-approval"}


def cmd_approve_record(args):
    with locked_project(args.project_root) as (root, state):
        ensure(not state["pending_impact"], "Unresolved upstream impact")
        if args.kind in {"ensemble-design", "extra-design"}:
            return ensemble.approve(_runtime(), args, root, state)
        if args.kind in phased.KINDS:
            return phased.approve(_runtime(), args, root, state)
        ensure(args.kind != "prompt-package", "Prompt packages become ready after contract check")
        key = _record_key(args.kind, args.character_id, args.variant_id or "base")
        value = state["records"].get(key)
        ensure(value and not value.get("stale"), f"Record is missing or stale: {key}")
        ensure(digest(read_json(root / value["path"])) == value["sha256"],
               "Record contents changed after submission")
        ensure(not read_json(root / value["path"])["unresolved"],
               "Resolve pending design decisions before approval")
        if args.kind == "design-card":
            card = read_json(root / value["path"])
            if card.get("schema_version") in {"CharacterDesignCardV2.2", "CharacterDesignCardV2.4"} and card.get("morphology") in {"human", "humanoid"}:
                validate_body_proportion_anchors(card)
                validate_design_handoffs(card, root)
        if args.kind == "cast-plan":
            _require_approved(state, "visual-bible")
        elif args.kind == "design-card":
            _require_approved(state, "cast-plan")
        require_text({"operator": args.operator}, "operator")
        value["approval"] = {"operator": args.operator, "at": now(), "sha256": value["sha256"]}
        state["decisions"].append({"kind": "approve-record", "key": key,
                                   "operator": args.operator, "at": now(),
                                   "sha256": value["sha256"]})
        return {"key": key, "approved": True}


def cmd_import_reference(args):
    source = Path(args.path).expanduser().resolve()
    ensure(source.is_file() and source.suffix.lower() in IMAGE_SUFFIXES,
           "Reference must be PNG, JPG or WebP")
    with locked_project(args.project_root) as (root, state):
        if args.character_id:
            ensure(args.character_id in {x["id"] for x in state["roster"]}, "Unknown character")
        ident = digest(source)[:16]
        target = root / "references" / f"{ident}{source.suffix.lower()}"
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copy2(source, target)
        row = {"id": ident, "path": str(target.relative_to(root)), "sha256": digest(source),
               "role": args.role, "desired_strength": args.desired_strength,
               "character_id": args.character_id, "imported_at": now()}
        if not any(x["id"] == ident and x["role"] == args.role for x in state["references"]):
            state["references"].append(row)
        return row


def cmd_import_image(args):
    source = Path(args.path).expanduser().resolve()
    ensure(source.is_file() and source.suffix.lower() in IMAGE_SUFFIXES,
           "Image must be PNG, JPG or WebP")
    with locked_project(args.project_root) as (root, state):
        ensure(args.stage in pipeline_stages(state), "Image stage is unavailable in this project pipeline")
        ensure(not state["pending_impact"], "Resolve upstream impact first")
        variant_id = args.variant_id or "base"
        key = _record_key("prompt-package", args.character_id, variant_id, args.stage)
        _require_approved(state, key)
        sha = digest(source)
        ident = (f"{args.character_id}-{variant_id}-{args.stage}-{sha[:16]}"
                 if state.get("pipeline_version", 1) >= 2 else f"{args.stage}-{sha[:16]}")
        roster_item = next((x for x in state["roster"] if x["id"] == args.character_id), None)
        ensure(roster_item is not None, "Unknown character ID")
        asset_mode = ensemble.mode(_runtime(), root, state, args.character_id)
        if asset_mode in {"ensemble", "speaking_extra"}:
            ensure(args.stage == "execution", "An extra has only one execution image per state")
        asset_name = safe_asset_label(roster_item["name"])
        state_name = safe_asset_label(variant_name(state, args.character_id, variant_id))
        stage_name = {"avatar": "头像", "expression": "九宫格表情", "full_body": "全身模卡",
                      "costume_design": "服饰设计", "execution": "执行资产"}[args.stage]
        if args.stage == "execution" and asset_mode in {"ensemble", "speaking_extra"}:
            stage_name = "群像执行资产" if asset_mode == "ensemble" else "独立执行资产"
        filename = f"{asset_name}_{state_name}_{stage_name}_{sha[:12]}{source.suffix.lower()}"
        target = root / "images" / args.character_id / variant_id / args.stage / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copy2(source, target)
        existing = next((x for x in state["images"] if x["id"] == ident and
                         x["character_id"] == args.character_id and
                         x["variant_id"] == variant_id), None)
        if existing:
            return existing
        row = {"id": ident, "stage": args.stage, "character_id": args.character_id,
               "variant_id": variant_id, "asset_name": roster_item["name"],
               "variant_name": variant_name(state, args.character_id, variant_id),
               "path": str(target.relative_to(root)),
               "sha256": sha, "prompt_sha256": state["records"][key]["sha256"],
               "imported_at": now(), "approval": None, "stale": False}
        row["purpose"] = read_json(root / state["records"][key]["path"]).get("purpose", "production")
        state["images"].append(row)
        return row


def _image(state, ident):
    item = next((x for x in state["images"] if x["id"] == ident), None)
    ensure(item, f"Unknown image: {ident}")
    ensure(not item.get("stale"), f"Image is stale: {ident}")
    return item


def cmd_submit_review(args):
    with locked_project(args.project_root) as (root, state):
        image = _image(state, args.image_id)
        ensure(digest(root / image["path"]) == image["sha256"],
               "Imported image contents changed")
        report = read_json(args.file)
        ensure(report.get("schema_version") == "CharacterImageReviewV1", "Wrong review schema")
        ensure(report.get("image_sha256") == image["sha256"] and
               report.get("stage") == image["stage"], "Review target mismatch")
        ensure(report.get("verdict") in {"pass", "revise", "uncertain"}, "Invalid verdict")
        for key in ("factual_conflicts", "identity_issues", "layout_issues",
                    "label_issues", "blocking_issues", "adoption_proposals"):
            require_list(report, key)
        if report["verdict"] == "pass":
            ensure(not report["blocking_issues"] and not report["factual_conflicts"] and
                   not report["identity_issues"] and not report["layout_issues"] and
                   not report["label_issues"], "A passing review cannot contain unresolved defects")
        review_sha = digest(report)
        path = root / "reviews" / f"{image['id']}-{review_sha[:12]}.json"
        write_json(path, report)
        state["reviews"][image["id"]] = {"path": str(path.relative_to(root)),
                                          "sha256": review_sha, "submitted_at": now()}
        image["approval"] = None
        return {"image_id": image["id"], "verdict": report["verdict"],
                "review_sha256": review_sha}


def cmd_approve_image(args):
    with locked_project(args.project_root) as (root, state):
        ensure(not state["pending_impact"], "Unresolved upstream impact")
        image = _image(state, args.image_id)
        ensure(image.get("purpose", "production") != "preview", "Use promote-candidate to explicitly adopt a preview")
        if phased.enabled(state):
            prompt_key = _record_key("prompt-package", image["character_id"], image["variant_id"], image["stage"])
            prompt = _checked_record(root, state, prompt_key)
            ensure(prompt["sha256"] == image["prompt_sha256"], "Image prompt version changed")
            if ensemble.mode(_runtime(), root, state, image["character_id"]) in {"ensemble", "speaking_extra"}:
                ensemble.resolve(_runtime(), root, state, read_json(root / prompt["path"]),
                                 image["character_id"], image["variant_id"])
            else:
                phased.resolve_basis(_runtime(), root, state, read_json(root / prompt["path"]), image["character_id"],
                                     image["variant_id"], image["stage"], force_approved=True)
        entry = state["reviews"].get(image["id"])
        ensure(entry, "Image must be reviewed first")
        ensure(digest(root / image["path"]) == image["sha256"],
               "Imported image contents changed")
        report = read_json(root / entry["path"])
        ensure(digest(report) == entry["sha256"], "Review contents changed")
        ensure(report["verdict"] == "pass" and not report["blocking_issues"],
               "Image review has not passed")
        require_text({"operator": args.operator}, "operator")
        previous = [x for x in state["images"] if x is not image and x["stage"] == image["stage"]
                    and x["character_id"] == image["character_id"] and
                    x["variant_id"] == image["variant_id"] and x.get("approval")]
        if previous:
            modern = state.get("pipeline_version", 1) >= 2
            if modern and image["stage"] in IDENTITY_STAGES:
                following = {"avatar": "expression", "expression": "full_body",
                             "full_body": "execution" if state.get("pipeline_version", 1) >= 3 else "costume_design"}[image["stage"]]
                _invalidate(state, image["character_id"], None, following)
            elif image["stage"] == "avatar":
                _invalidate(state, image["character_id"], image["variant_id"], "expression")
                _invalidate(state, image["character_id"], image["variant_id"], "full_body")
            elif image["stage"] != "execution":
                _invalidate(state, image["character_id"], image["variant_id"], "execution")
            for old in previous:
                old["approval"] = None
        image["approval"] = {"operator": args.operator, "at": now(),
                             "image_sha256": image["sha256"],
                             "review_sha256": entry["sha256"]}
        state["decisions"].append({"kind": "approve-image", "image_id": image["id"],
                                   "operator": args.operator, "at": now(),
                                   "image_sha256": image["sha256"],
                                   "review_sha256": entry["sha256"]})
        return {"image_id": image["id"], "approved": True}


def cmd_refresh(args):
    with locked_project(args.project_root) as (root, state):
        ensure(not state["pending_impact"], "Resolve current impact before another refresh")
        revision = state["revision"] + 1
        old_roster = {x["id"]: x for x in state["roster"]}
        inputs = copy.deepcopy(state["inputs"])
        changed = []
        new_data = {}
        for kind, path in (("screenplay", args.screenplay), ("asset_table", args.asset_table),
                           ("scene_log", args.scene_log)):
            if path:
                candidate = Path(path).expanduser().resolve()
                if inputs.get(kind, {}).get("sha256") != digest(candidate):
                    inputs[kind], new_data[kind] = _copy_input(root, kind, path, revision)
                    changed.append(kind)
        ensure(changed, "No changed input files")
        if "asset_table" in changed:
            roster = roster_from_assets(new_data["asset_table"])
            new_ids = {x["id"] for x in roster}
            direct = [x["id"] for x in roster if old_roster.get(x["id"], {}).get("asset_digest")
                      != x["asset_digest"]]
            removed = sorted(set(old_roster) - new_ids)
            state["roster"] = roster
        else:
            direct, removed = [], []
        for ident in set(direct + removed):
            _invalidate(state, ident, None, "design-card")
        state["inputs"] = inputs
        state["pending_impact"] = {"changed_inputs": changed,
                                   "directly_changed_characters": direct,
                                   "removed_characters": removed,
                                   "needs_context_review": "screenplay" in changed or "scene_log" in changed,
                                   "created_at": now()}
        return state["pending_impact"]


def cmd_resolve_impact(args):
    with locked_project(args.project_root) as (_root, state):
        ensure(state["pending_impact"], "No pending upstream impact")
        known = {x["id"] for x in state["roster"]}
        affected = set(args.affected or [])
        ensure(affected <= known, f"Unknown affected IDs: {sorted(affected - known)}")
        if args.global_style:
            _invalidate(state, start="visual-bible")
        else:
            for ident in affected:
                _invalidate(state, ident, None, "design-card")
        state["decisions"].append({"kind": "resolve-impact", "operator": args.operator,
                                   "at": now(), "affected": sorted(affected),
                                   "global_style": bool(args.global_style),
                                   "reviewed_inputs": state["pending_impact"]["changed_inputs"]})
        state["pending_impact"] = None
        return {"affected": sorted(affected), "global_style": bool(args.global_style)}


def cmd_package(args):
    root = Path(args.project_root).expanduser().resolve()
    state = read_json(root / "project.json")
    if ensemble.mode(_runtime(), root, state, args.character_id) in {"ensemble", "speaking_extra"}:
        return ensemble.package(_runtime(), args, root, state)
    ensure(not state["pending_impact"], "Unresolved upstream impact")
    ident = args.character_id
    variant = args.variant_id or "base"
    variant_name(state, ident, variant)
    modern = state.get("pipeline_version", 1) >= 2
    for kind, source in state["inputs"].items():
        ensure(digest(root / source["path"]) == source["sha256"],
               f"Imported {kind} file changed after intake")
    _checked_record(root, state, "visual-bible")
    _checked_record(root, state, "cast-plan")
    card_variants = ([variant] if phased.enabled(state) else
                     ["base", variant] if modern and variant != "base" else [variant])
    records = [_checked_record(root, state, _record_key("design-card", ident, v))
               for v in card_variants]
    phase_keys = []
    if phased.enabled(state):
        phase_keys = ["script-context", *phased.basis_keys(ident, variant, "execution", state)[:-1]]
        records.extend(_checked_record(root, state, item) for item in phase_keys)
    images = []
    for stage in pipeline_stages(state):
        stage_variant = "base" if modern and stage in IDENTITY_STAGES else variant
        records.append(_checked_record(root, state, _record_key("prompt-package", ident, stage_variant, stage)))
        images.append(_checked_image(root, state, stage, ident, stage_variant))
    legacy_identity_keys = sorted({x["migration_legacy_identity"]["card_key"] for x in images
                                   if x.get("migration_legacy_identity")})
    records.extend(_checked_record(root, state, item) for item in legacy_identity_keys)
    out = Path(args.output).expanduser().resolve()
    ensure(not out.exists(), f"Output already exists: {out}")
    out.mkdir(parents=True)
    copied = []
    for item in [state["records"]["visual-bible"], state["records"]["cast-plan"], *records]:
        source = root / item["path"]
        target = out / item["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied.append({"path": str(target.relative_to(out)), "sha256": digest(target)})
    for image in images:
        review = state["reviews"][image["id"]]
        for item in (image, review):
            source = root / item["path"]
            target = out / item["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            copied.append({"path": str(target.relative_to(out)), "sha256": digest(target)})
    if phased.enabled(state):
        for item in phase_keys:
            if not item.startswith("stage-design:"):
                continue
            data = read_json(root / state["records"][item]["path"])
            for work in data["specialist_execution"].values():
                for knowledge in work.get("knowledge_refs", []):
                    source = root / "knowledge-snapshots" / knowledge["sha256"]
                    ensure(source.is_file() and digest(source) == knowledge["sha256"], "Knowledge snapshot changed before packaging")
                    target = out / "knowledge-snapshots" / knowledge["sha256"]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, target)
                    if not any(x["path"] == str(target.relative_to(out)) for x in copied):
                        copied.append({"path": str(target.relative_to(out)), "sha256": digest(target)})
                if work.get("mode") != "independent":
                    continue
                source = root / work["proposal_ref"]
                ensure(digest(source) == work["proposal_sha256"], "Specialist proposal changed before packaging")
                target = out / work["proposal_ref"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
                if not any(x["path"] == str(target.relative_to(out)) for x in copied):
                    copied.append({"path": str(target.relative_to(out)), "sha256": digest(target)})
                proposal = read_json(source)
                for knowledge in (proposal.get("knowledge_refs", [])
                                  if proposal.get("schema_version") == "CharacterSpecialistProposalV1.2" else []):
                    knowledge_source = root / "knowledge-snapshots" / knowledge["sha256"]
                    ensure(knowledge_source.is_file() and digest(knowledge_source) == knowledge["sha256"],
                           "Independent knowledge snapshot changed before packaging")
                    knowledge_target = out / "knowledge-snapshots" / knowledge["sha256"]
                    knowledge_target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(knowledge_source, knowledge_target)
                    if not any(x["path"] == str(knowledge_target.relative_to(out)) for x in copied):
                        copied.append({"path": str(knowledge_target.relative_to(out)), "sha256": digest(knowledge_target)})
    relevant_refs = [x for x in state["references"] if x.get("character_id") in
                     {None, ident}]
    for item in relevant_refs:
        source = root / item["path"]
        ensure(digest(source) == item["sha256"],
               f"Reference image contents changed: {item['id']}")
        target = out / item["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied.append({"path": str(target.relative_to(out)), "sha256": digest(target)})
    plugin_root = Path(__file__).resolve().parents[1]
    for relative in ("knowledge/source-register.json", "sources.lock.json"):
        source = plugin_root / relative
        ensure(source.is_file(), f"Plugin provenance file missing: {relative}")
        target = out / "plugin-provenance" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied.append({"path": str(target.relative_to(out)), "sha256": digest(target)})
    image_ids = {x["id"] for x in images}
    record_keys = {"visual-bible", "cast-plan"}
    record_keys.update(phase_keys)
    record_keys.update(legacy_identity_keys)
    record_keys.update(_record_key("design-card", ident, v) for v in card_variants)
    record_keys.update(_record_key("prompt-package", ident,
                                   "base" if modern and stage in IDENTITY_STAGES else variant, stage)
                       for stage in pipeline_stages(state))
    manifest = {"schema_version": "CharacterAssetPackV3" if state.get("pipeline_version", 1) >= 3 else
                               "CharacterAssetPackV2" if modern else "CharacterAssetPackV1",
                "plugin_version": PLUGIN_VERSION,
                "project_id": state["project_id"],
                "character_id": ident, "asset_name": next(x["name"] for x in state["roster"] if x["id"] == ident),
                "variant_id": variant, "variant_name": variant_name(state, ident, variant),
                "legacy_identity_basis": {x["stage"]: x["migration_legacy_identity"] for x in images
                                          if x.get("migration_legacy_identity")},
                "created_at": now(),
                "input_sources": state["inputs"],
                "approved_images": {x["stage"]: {"path": x["path"], "sha256": x["sha256"],
                                                  "approval": x["approval"],
                                                  "purpose": {"avatar": "身份锚点",
                                                              "expression": "剧情表情参考",
                                                              "full_body": "完整全身身份模卡",
                                                              "costume_design": "当前变体服饰设计",
                                                              "execution": "制作执行参考板"}[x["stage"]]}
                                    for x in images},
                "record_approvals": {key: state["records"][key]["approval"]
                                     for key in sorted(record_keys)},
                "files": copied, "decisions": [x for x in state["decisions"]
                                                if x.get("key") in record_keys or
                                                x.get("image_id") in image_ids],
                "reference_images": relevant_refs}
    manifest["design_progression"] = state.get("design_progression", "complete")
    if phased.enabled(state):
        context = read_json(root / state["records"]["script-context"]["path"])
        manifest["context_source_receipt"] = {"source_sha256": context["source_sha256"],
                                                "context_sha256": state["records"]["script-context"]["sha256"],
                                                "read_units": len(context["read_units"])}
    write_json(out / "manifest.json", manifest)
    return {"asset_pack": str(out), "files": len(copied) + 1}


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="Import project sources")
    init.add_argument("--project-root", required=True)
    init.add_argument("--project-id")
    init.add_argument("--screenplay")
    init.add_argument("--asset-table")
    init.add_argument("--scene-log")
    init.add_argument("--snapshot", help="Approved AssetProjectSnapshotV1 from the parent plugin")
    init.add_argument("--design-progression", choices=("phased", "complete"), default="phased")
    context = sub.add_parser("context-units", help="Enumerate the complete source for reading coverage")
    context.add_argument("--project-root")
    context.add_argument("--source", help="Standalone screenplay or biography; no asset table required")
    context.add_argument("--output")
    status = sub.add_parser("status")
    status.add_argument("--project-root", required=True)
    upgrade = sub.add_parser("upgrade-pipeline", help="Explicitly migrate an eligible phased V2 project to the four-image V3 pipeline")
    upgrade.add_argument("--project-root", required=True)
    upgrade.add_argument("--operator", required=True)
    plan = sub.add_parser("plan", help="Read-only stage queue for one character or the full roster")
    plan.add_argument("--project-root", required=True)
    plan.add_argument("--character-id", action="append", help="Repeat to plan a selected batch; omit for all")
    plan.add_argument("--variant-id")
    plan.add_argument("--stage", choices=STAGES)
    submit = sub.add_parser("submit", help="Register a structured design/prompt draft")
    submit.add_argument("--project-root", required=True)
    submit.add_argument("--kind", choices=("visual-bible", "cast-plan", "design-card", "ensemble-design", "extra-design", "prompt-package", *sorted(phased.KINDS)), required=True)
    submit.add_argument("--file", required=True)
    submit.add_argument("--character-id")
    submit.add_argument("--variant-id", default="base")
    submit.add_argument("--stage", choices=STAGES)
    submit.add_argument("--scope", choices=sorted(phased.SCOPES))
    approve = sub.add_parser("approve-record")
    approve.add_argument("--project-root", required=True)
    approve.add_argument("--kind", choices=("visual-bible", "cast-plan", "design-card", "ensemble-design", "extra-design", *sorted(phased.KINDS)), required=True)
    approve.add_argument("--character-id")
    approve.add_argument("--variant-id", default="base")
    approve.add_argument("--operator", required=True)
    approve.add_argument("--scope", choices=sorted(phased.SCOPES))
    compile_card = sub.add_parser("compile-design-card", help="Compose approved scope snapshots without new creative decisions")
    compile_card.add_argument("--project-root", required=True)
    compile_card.add_argument("--character-id", required=True)
    compile_card.add_argument("--variant-id", default="base")
    promote = sub.add_parser("promote-candidate", help="Explicitly approve an unchanged, reviewed avatar preview")
    promote.add_argument("--project-root", required=True)
    promote.add_argument("--image-id", required=True)
    promote.add_argument("--operator", required=True)
    promote.add_argument("--approve-design-basis", action="store_true", help="Explicitly approve the exact bound brief and identity snapshot")
    reference = sub.add_parser("import-reference")
    reference.add_argument("--project-root", required=True)
    reference.add_argument("--path", required=True)
    reference.add_argument("--role", choices=("identity", "costume", "style", "inspiration"), required=True)
    reference.add_argument("--desired-strength", required=True)
    reference.add_argument("--character-id")
    image = sub.add_parser("import-image")
    image.add_argument("--project-root", required=True)
    image.add_argument("--path", required=True)
    image.add_argument("--stage", choices=STAGES, required=True)
    image.add_argument("--character-id", required=True)
    image.add_argument("--variant-id", default="base")
    review = sub.add_parser("submit-review")
    review.add_argument("--project-root", required=True)
    review.add_argument("--image-id", required=True)
    review.add_argument("--file", required=True)
    approve_image = sub.add_parser("approve-image")
    approve_image.add_argument("--project-root", required=True)
    approve_image.add_argument("--image-id", required=True)
    approve_image.add_argument("--operator", required=True)
    refresh = sub.add_parser("refresh")
    refresh.add_argument("--project-root", required=True)
    refresh.add_argument("--screenplay")
    refresh.add_argument("--asset-table")
    refresh.add_argument("--scene-log")
    impact = sub.add_parser("resolve-impact")
    impact.add_argument("--project-root", required=True)
    impact.add_argument("--affected", nargs="*")
    impact.add_argument("--global-style", action="store_true")
    impact.add_argument("--operator", required=True)
    release = sub.add_parser("package")
    release.add_argument("--project-root", required=True)
    release.add_argument("--character-id", required=True)
    release.add_argument("--variant-id", default="base")
    release.add_argument("--output", required=True)
    return parser


def main():
    args = build_parser().parse_args()
    actions = {"init": cmd_init, "status": cmd_status, "upgrade-pipeline": cmd_upgrade_pipeline,
               "plan": cmd_plan, "submit": cmd_submit,
               "context-units": lambda args: phased.context_units(_runtime(), args),
               "compile-design-card": lambda args: phased.compile_card(_runtime(), args),
               "promote-candidate": lambda args: phased.promote(_runtime(), args),
               "approve-record": cmd_approve_record, "import-reference": cmd_import_reference,
               "import-image": cmd_import_image, "submit-review": cmd_submit_review,
               "approve-image": cmd_approve_image, "refresh": cmd_refresh,
               "resolve-impact": cmd_resolve_impact, "package": cmd_package}
    try:
        print(json.dumps(actions[args.command](args), ensure_ascii=False, indent=2))
    except (ValueError, KeyError, OSError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
