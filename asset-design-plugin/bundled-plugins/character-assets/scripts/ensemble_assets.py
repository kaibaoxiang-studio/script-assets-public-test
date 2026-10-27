"""One-image production paths for extras in a V3 character project.

The asset-table row remains the stable ID. A group design describes the people
visible in one image; it never turns representative extras into new story facts.
"""
from __future__ import annotations

from pathlib import Path
import re
import shutil


def key(character, variant):
    return f"ensemble-design:{character}:{variant}"


def extra_key(character, variant):
    return f"extra-design:{character}:{variant}"


def design_key(asset_mode, character, variant):
    return extra_key(character, variant) if asset_mode == "speaking_extra" else key(character, variant)


def _style_anchors(style):
    if isinstance(style, str) and style.strip():
        return [style.strip()]
    if isinstance(style, dict):
        values = []
        for value in style.values():
            values.extend(_style_anchors(value))
        return values
    if isinstance(style, list):
        values = []
        for value in style:
            values.extend(_style_anchors(value))
        return values
    return []


def _script_count(row, screenplay=None, variant=None):
    """Recognize only an unambiguous local numeral near the group name."""
    numerals = {"一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5,
                "六": 6, "七": 7, "八": 8, "九": 9}

    def number(token):
        if token.isdigit():
            return int(token)
        if token == "十":
            return 10
        if "十" in token:
            high, low = token.split("十", 1)
            return (numerals.get(high, 1) if high else 1) * 10 + (numerals.get(low, 0) if low else 0)
        return numerals[token]

    counts = set()
    amount = r"(\d+|[一二两三四五六七八九十]{1,3})"
    unit = r"[名个位人]"
    name = re.escape(row["name"])
    states = [x for x in row.get("states", []) if variant is None or x.get("id") == variant]
    evidence = [item for part in states for item in part.get("evidence", [])]
    texts = [item.get("text", "") for item in evidence]
    refs = {ref for item in evidence for ref in item.get("source_refs", [])}
    if isinstance(screenplay, dict) and refs:
        for episode in screenplay.get("episodes", []):
            for scene in episode.get("scenes", []):
                for block in scene.get("blocks", []):
                    if refs.intersection(block.get("source_refs", [])):
                        texts.append(block.get("text", ""))
    for source in texts:
        for pattern in (amount + r"\s*" + unit + r"\s*" + name,
                        name + r"\s*" + amount + r"\s*" + unit):
            for match in re.finditer(pattern, source):
                counts.add(number(match.group(1)))
    if len(counts) > 1:
        raise ValueError(f"Conflicting explicit group counts for {row['name']}: {sorted(counts)}")
    return next(iter(counts)) if counts else None


def _speaker_names(cp, root, state):
    source = root / state["inputs"]["screenplay"]["path"]
    screenplay = cp.load_source(source)
    cp.ensure(isinstance(screenplay, dict) and isinstance(screenplay.get("episodes"), list),
              "Classifying extras by dialogue needs a structured screenplay JSON with episodes/scenes/blocks")
    speakers = set()
    for episode in screenplay["episodes"]:
        for scene in episode.get("scenes", []):
            for block in scene.get("blocks", []):
                if block.get("type") == "dialogue" and isinstance(block.get("speaker"), str):
                    speakers.add(re.sub(r"\s+", "", block["speaker"]))
    return speakers


def mode(cp, root, state, character):
    """Return individual, speaking_extra or ensemble; preserve old approved work."""
    if state.get("pipeline_version", 1) < 3 or not state.get("design_progression") == "phased":
        return "individual"
    row = next((x for x in state["roster"] if x["id"] == character), None)
    cp.ensure(row is not None, f"Unknown character ID: {character}")
    if row.get("tier") not in {"群演", "群像"}:
        return "individual"
    if any(x.get("character_id") == character and x.get("approval") and
           x.get("stage") in cp.IDENTITY_STAGES for x in state["images"]):
        return "individual"
    if any(k.startswith((f"stage-design:identity:{character}:", f"design-card:{character}:")) and
           v.get("approval") for k, v in state["records"].items()):
        return "individual"
    names = {re.sub(r"\s+", "", x) for x in [row["name"], *row.get("aliases", [])] if x}
    speakers = _speaker_names(cp, root, state)
    if names & speakers:
        return "speaking_extra"
    ambiguous = sorted(s for s in speakers for n in names
                       if s.startswith(n) and s != n and
                       re.fullmatch(r"[甲乙丙丁一二三四五六七八九十\dA-Za-z]+", s[len(n):]))
    cp.ensure(not ambiguous,
              f"Group asset {character} contains individually speaking members {ambiguous}; split them into asset IDs")
    return "ensemble"


def validate(cp, root, state, data, character, variant):
    cp.ensure(mode(cp, root, state, character) == "ensemble", "Only non-speaking group extras use ensemble-design")
    cp.ensure(data.get("schema_version") == "GroupEnsembleDesignV1" and
              data.get("character_id") == character and data.get("variant_id") == variant,
              "Group design target/schema mismatch")
    cp.require_known_variant(state, character, variant)
    expected = {x: cp._checked_record(root, state, x)["sha256"] for x in
                ("script-context", "visual-bible", "cast-plan")}
    cp.ensure(data.get("parent_refs") == expected, "Group design must bind current script, cast and visual style")
    cp.require_text(data, "narrative_function")
    cp.require_text(data, "world_style_translation")
    cp.require_text(data, "shared_visual_grammar")
    cp.require_text(data, "variation_logic")
    cp.require_text(data, "quantity_basis")
    cp.require_text(data, "arrangement")
    cp.require_list(data, "source_refs")
    cp.ensure(data["source_refs"], "Group design needs script source_refs")
    row = next(x for x in state["roster"] if x["id"] == character)
    bible = cp.read_json(root / state["records"]["visual-bible"]["path"])
    style_anchors = _style_anchors(bible["style"])
    cp.ensure(all(anchor in data["world_style_translation"] for anchor in style_anchors),
              "Group design must carry the approved project visual style")
    known_refs = {ref for item in row.get("states", []) for e in item.get("evidence", [])
                  for ref in e.get("source_refs", [])}
    if known_refs:
        cp.ensure(set(data["source_refs"]) & known_refs,
                  "Group source_refs must include an asset-table script reference")
    cp.ensure(data.get("quantity_status") in {"script_explicit", "representative_choice"},
              "Group quantity must distinguish script count from representative choice")
    count = data.get("member_count")
    cp.ensure(type(count) is int and count >= 1, "Group member_count must be a positive integer")
    explicit = data.get("script_count")
    cp.ensure(explicit is None or type(explicit) is int and explicit >= 1,
              "script_count must be a positive number or null")
    if explicit is not None:
        cp.ensure(data["quantity_status"] == "script_explicit" and count == explicit,
                  "A script-explicit group must show exactly the scripted number")
    else:
        cp.ensure(data["quantity_status"] == "representative_choice",
                  "Unknown group size requires a labeled representative choice")
    screenplay = cp.load_source(root / state["inputs"]["screenplay"]["path"])
    found_count = _script_count(row, screenplay, variant)
    if found_count is not None:
        cp.ensure(explicit == found_count and count == found_count,
                  "Group figure count must match the explicit asset-table script evidence")
    members = data.get("members")
    cp.ensure(isinstance(members, list) and len(members) == count,
              "Group design needs one concrete member per depicted person")
    slots = []
    for member in members:
        for field in ("slot", "body_and_posture", "face_and_hair", "costume_structure",
                      "color_and_material", "action_or_prop"):
            cp.require_text(member, field)
        cp.ensure(member.get("evidence_status") in {"script_fact", "inference", "creative_choice", "mixed"},
                  "Each member needs an evidence boundary")
        slots.append(member["slot"])
    cp.ensure(len(slots) == len(set(slots)), "Group member slots must be unique")
    cp.ensure(len({m["body_and_posture"] + m["face_and_hair"] for m in members}) == count,
              "Group members cannot all reuse the same face and build")
    cp.require_list(data, "unresolved")
    cp.ensure(data.get("new_lore_policy") in {"none", "pending_approval"},
              "New group lore must be explicitly identified")
    if data["new_lore_policy"] == "pending_approval":
        cp.ensure(data["unresolved"], "Unapproved new lore cannot be silently finalized")


def validate_extra(cp, root, state, data, character, variant):
    cp.ensure(mode(cp, root, state, character) == "speaking_extra",
              "Only speaking extras use extra-design")
    cp.ensure(data.get("schema_version") == "SpeakingExtraDesignV1" and
              data.get("character_id") == character and data.get("variant_id") == variant,
              "Speaking extra design target/schema mismatch")
    cp.require_known_variant(state, character, variant)
    expected = {x: cp._checked_record(root, state, x)["sha256"] for x in
                ("script-context", "visual-bible", "cast-plan")}
    cp.ensure(data.get("parent_refs") == expected,
              "Speaking extra design must bind current script, cast and visual style")
    for field in ("narrative_function", "spoken_line", "world_style_translation", "face_and_hair",
                  "body_and_posture", "costume_front", "costume_back", "color_and_material",
                  "prop_and_action"):
        cp.require_text(data, field)
    screenplay = cp.load_source(root / state["inputs"]["screenplay"]["path"])
    row = next(x for x in state["roster"] if x["id"] == character)
    names = {re.sub(r"\s+", "", x) for x in [row["name"], *row.get("aliases", [])] if x}
    spoken = [(block.get("text", ""), block.get("source_refs", []))
              for episode in screenplay["episodes"] for scene in episode.get("scenes", [])
              for block in scene.get("blocks", []) if block.get("type") == "dialogue" and
              re.sub(r"\s+", "", block.get("speaker", "")) in names]
    cp.ensure(any(data["spoken_line"] in text for text, _ in spoken),
              "Speaking extra design must quote a scripted line")
    cp.require_list(data, "source_refs")
    cp.ensure(data["source_refs"] and any(set(data["source_refs"]) & set(refs) for _, refs in spoken),
              "Speaking extra source_refs must include its dialogue source")
    bible = cp.read_json(root / state["records"]["visual-bible"]["path"])
    cp.ensure(all(anchor in data["world_style_translation"] for anchor in _style_anchors(bible["style"])),
              "Speaking extra must carry approved project visual style")
    cp.ensure(data.get("evidence_status") in {"script_fact", "inference", "creative_choice", "mixed"},
              "Speaking extra design needs an evidence boundary")
    cp.require_list(data, "unresolved")
    cp.ensure(data.get("new_lore_policy") in {"none", "pending_approval"},
              "New lore must be explicitly identified")
    if data["new_lore_policy"] == "pending_approval":
        cp.ensure(data["unresolved"], "Unapproved new lore cannot be silently finalized")


def submit(cp, args, root, state):
    data = cp.read_json(args.file)
    character, variant = args.character_id, args.variant_id or "base"
    speaking = args.kind == "extra-design"
    (validate_extra if speaking else validate)(cp, root, state, data, character, variant)
    record_key = extra_key(character, variant) if speaking else key(character, variant)
    sha = cp.digest(data)
    prior = state["records"].get(record_key)
    if prior and prior["sha256"] == sha and not prior.get("stale"):
        return {"key": record_key, "status": "unchanged", "sha256": sha}
    if prior:
        cp._invalidate(state, character, variant, args.kind)
    path = root / "records" / record_key.replace(":", "/") / f"{sha[:12]}.json"
    cp.write_json(path, data)
    state["records"][record_key] = {"path": str(path.relative_to(root)), "sha256": sha,
                                    "submitted_at": cp.now(), "approval": None, "stale": False}
    return {"key": record_key, "sha256": sha, "status": "awaiting-approval"}


def approve(cp, args, root, state):
    character, variant = args.character_id, args.variant_id or "base"
    speaking = args.kind == "extra-design"
    record_key = extra_key(character, variant) if speaking else key(character, variant)
    record = state["records"].get(record_key)
    cp.ensure(record and not record.get("stale"), f"Missing group design: {record_key}")
    data = cp.read_json(root / record["path"])
    cp.ensure(cp.digest(data) == record["sha256"], "Group design changed after submission")
    (validate_extra if speaking else validate)(cp, root, state, data, character, variant)
    cp.ensure(not data["unresolved"], "Resolve group design decisions before approval")
    cp.require_text({"operator": args.operator}, "operator")
    record["approval"] = {"operator": args.operator, "at": cp.now(), "sha256": record["sha256"]}
    state["decisions"].append({"kind": "approve-record", "key": record_key, **record["approval"]})
    return {"key": record_key, "approved": True, "sha256": record["sha256"]}


def resolve(cp, root, state, package, character, variant):
    asset_mode = mode(cp, root, state, character)
    cp.ensure(asset_mode in {"ensemble", "speaking_extra"}, "This asset uses the multi-stage route")
    record_key = design_key(asset_mode, character, variant)
    record = cp._checked_record(root, state, record_key)
    supplied = package.get("design_basis", {}).get("records")
    cp.ensure(supplied == {record_key: record["sha256"]},
              "Group prompt must bind the current approved group design")
    data = cp.read_json(root / record["path"])
    (validate_extra if asset_mode == "speaking_extra" else validate)(cp, root, state, data, character, variant)
    return data


def validate_prompt(cp, package, design):
    cp.ensure(package.get("morphology") == "group", "Group prompt morphology must be group")
    cp.ensure(package.get("anchor_images") == {}, "Group sheet has no individual identity image anchors")
    count = design["member_count"]
    layout = package.get("layout") or {}
    slots = [x["slot"] for x in design["members"]]
    cp.ensure(layout.get("type") == "ensemble_lineup" and layout.get("single_canvas") is True and
              layout.get("full_body") is True and layout.get("member_count") == count and
              layout.get("ordered_slots") == slots,
              "Group layout must show every member full body on one canvas in approved order")
    cp.ensure(not any(k in layout for k in ("top_left", "top_right", "bottom_left", "bottom_right")),
              "Group image cannot use a four-panel individual layout")
    ratio = package.get("aspect_ratio")
    cp.ensure(isinstance(ratio, str) and re.fullmatch(r"[1-9]\d*:[1-9]\d*", ratio),
              "Group prompt needs a numeric aspect_ratio")
    wide, tall = map(int, ratio.split(":"))
    if count > 1:
        cp.ensure(wide > tall, "Multiple extras need a horizontal canvas")
    else:
        cp.ensure(ratio == "9:16", "A single non-speaking extra uses a 9:16 full-body canvas")
    cp.require_text(package, "aspect_ratio_basis")
    cp.ensure(design["world_style_translation"] in "\n".join(x["text"] for x in package["prompts"]),
              "Group prompt must carry the approved style translation verbatim")
    for prompt in package["prompts"]:
        text = prompt["text"]
        cp.ensure(ratio in text and str(count) in text and all(slot in text for slot in slots),
                  "Group prompt must state ratio, exact depicted count and ordered member slots")
        cp.ensure("全身" in text and "风格" in text,
                  "Group prompt must state full-body visibility and project visual style")
    checks = "\n".join(package["acceptance_checks"])
    cp.ensure(all(x in checks for x in (ratio, "人数", "全身", "顺序", "风格")),
              "Group review must check canvas, count, full bodies, order and project style")


def validate_extra_prompt(cp, package, design):
    cp.ensure(package.get("morphology") == "human", "Speaking extra prompt must depict one human")
    cp.ensure(package.get("anchor_images") == {}, "Single-sheet extra has no identity image prerequisites")
    cp.ensure(package.get("aspect_ratio") == "9:16", "Speaking extra execution sheet must be 9:16")
    required_layout = {"top_left": "front_face", "top_right": "three_quarter_face_45",
                       "bottom_left": "headless_enlarged_front_costume",
                       "bottom_right": "complete_back_head_to_shoes"}
    cp.ensure(package.get("layout") == required_layout,
              "Speaking extra uses one 9:16 four-panel execution sheet")
    for prompt in package["prompts"]:
        content = prompt["text"]
        cp.ensure(all(token in content for token in
                      ("9:16", "正脸", "45", "无头", "背面")),
                  "Speaking extra prompt must state the one-sheet layout")
        cp.ensure(design["world_style_translation"] in content,
                  "Speaking extra prompt must carry approved style verbatim")
    checks = "\n".join(package["acceptance_checks"])
    cp.ensure(all(token in checks for token in ("9:16", "正脸", "45", "无头", "背面", "风格")),
              "Speaking extra review must check all four panels and project style")


def package(cp, args, root, state):
    character, variant = args.character_id, args.variant_id or "base"
    asset_mode = mode(cp, root, state, character)
    cp.ensure(asset_mode in {"ensemble", "speaking_extra"}, "This asset uses the multi-stage pack route")
    cp.ensure(not state["pending_impact"], "Unresolved upstream impact")
    cp.require_known_variant(state, character, variant)
    for source in state["inputs"].values():
        cp.ensure(cp.digest(root / source["path"]) == source["sha256"], "Imported source changed")
    record_key = design_key(asset_mode, character, variant)
    keys = ["script-context", "visual-bible", "cast-plan", record_key,
            cp._record_key("prompt-package", character, variant, "execution")]
    records = {k: cp._checked_record(root, state, k) for k in keys}
    image = cp._checked_image(root, state, "execution", character, variant)
    review = state["reviews"][image["id"]]
    out = Path(args.output).expanduser().resolve()
    cp.ensure(not out.exists(), f"Output already exists: {out}")
    out.mkdir(parents=True)
    copied = []
    for item in [*records.values(), image, review]:
        source = root / item["path"]
        target = out / item["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied.append({"path": str(target.relative_to(out)), "sha256": cp.digest(target)})
    refs = [x for x in state["references"] if x.get("character_id") in {None, character}]
    for item in refs:
        source = root / item["path"]
        cp.ensure(cp.digest(source) == item["sha256"], "Group reference changed")
        target = out / item["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied.append({"path": str(target.relative_to(out)), "sha256": cp.digest(target)})
    plugin_root = Path(cp.__file__).resolve().parents[1]
    for relative in ("knowledge/source-register.json", "sources.lock.json"):
        source = plugin_root / relative
        cp.ensure(source.is_file(), f"Missing plugin provenance: {relative}")
        target = out / "plugin-provenance" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied.append({"path": str(target.relative_to(out)), "sha256": cp.digest(target)})
    design = cp.read_json(root / records[record_key]["path"])
    manifest = {"schema_version": ("CharacterSpeakingExtraPackV1" if asset_mode == "speaking_extra"
                                    else "CharacterEnsemblePackV1"), "plugin_version": cp.PLUGIN_VERSION,
                "project_id": state["project_id"], "character_id": character,
                "asset_name": next(x["name"] for x in state["roster"] if x["id"] == character),
                "variant_id": variant, "variant_name": cp.variant_name(state, character, variant),
                "member_count": design.get("member_count", 1),
                "quantity_status": design.get("quantity_status", "scripted_speaker"),
                "approved_image": {"path": image["path"], "sha256": image["sha256"],
                                   "approval": image["approval"]},
                "record_approvals": {k: v["approval"] for k, v in records.items()},
                "input_sources": state["inputs"], "reference_images": refs,
                "files": copied, "created_at": cp.now(),
                "decisions": [x for x in state["decisions"] if x.get("key") in keys or x.get("image_id") == image["id"]]}
    cp.write_json(out / "manifest.json", manifest)
    return {"asset_pack": str(out), "files": len(copied) + 1}
