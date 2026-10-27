"""Synthetic, byte-accurate child-project state for import integrity tests."""
import base64
import hashlib
import json
from pathlib import Path
import shutil

FIXTURES = Path(__file__).resolve().parent / "fixtures"

def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def byte_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def character_project(root):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    inputs = {}
    for kind, filename in (("screenplay", "screenplay.json"), ("asset_table", "assets.json")):
        target = root / "inputs" / "rev-001" / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(FIXTURES / filename, target)
        inputs[kind] = {"path": str(target.relative_to(root)), "sha256": byte_hash(target), "format": "json", "original_name": filename}
    identity = {"schema_version": "CharacterStageDesignV1", "character_id": "CHR-001", "variant_id": "base", "scope": "identity", "payload": {"face": "略宽眼距，短圆下巴", "hair": "贴颈短卷发"}, "unresolved": []}
    identity_path = root / "records" / "identity.json"
    write_json(identity_path, identity)
    identity_hash = canonical_hash(identity)
    approval = {"operator": "human:original-owner", "at": "2026-10-22T09:00:00Z", "sha256": identity_hash}
    record = {"path": "records/identity.json", "sha256": identity_hash, "approval": approval, "stale": False}
    image_path = root / "images" / "avatar.png"
    image_path.parent.mkdir(parents=True, exist_ok=True)
    image_path.write_bytes(base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jULsAAAAASUVORK5CYII="))
    image_hash = byte_hash(image_path)
    review = {"schema_version": "CharacterImageReviewV1", "image_sha256": image_hash, "stage": "avatar", "verdict": "pass", "factual_conflicts": [], "identity_issues": [], "layout_issues": [], "label_issues": [], "blocking_issues": [], "adoption_proposals": []}
    review_path = root / "reviews" / "avatar.json"
    write_json(review_path, review)
    review_hash = canonical_hash(review)
    prompt = {"schema_version": "CharacterPromptPackageV1", "character_id": "CHR-001", "variant_id": "base", "stage": "avatar", "prompts": [{"id": "avatar", "prompt": "3:4未精修选角照，面部和发型按批准身份"}]}
    prompt_path = root / "records" / "prompt.json"
    write_json(prompt_path, prompt)
    prompt_hash = canonical_hash(prompt)
    image = {"id": "avatar-approved", "stage": "avatar", "character_id": "CHR-001", "variant_id": "base", "path": "images/avatar.png", "sha256": image_hash, "prompt_sha256": prompt_hash, "purpose": "production", "stale": False, "approval": {"operator": "human:original-owner", "at": "2026-10-22T09:02:00Z", "image_sha256": image_hash, "review_sha256": review_hash}}
    assets = json.loads((FIXTURES / "assets.json").read_text(encoding="utf-8"))
    roster = [{"id": x["id"], "name": x["name"], "tier": x.get("tier", "未分层"), "priority": "deep" if x["id"] == "CHR-001" else "light", "states": x["states"], "aliases": [], "asset_digest": canonical_hash(x)} for x in assets["characters"]]
    state = {"schema_version": "CharacterProjectV1", "pipeline_version": 3, "design_progression": "phased", "project_id": "original-character-project", "revision": 7, "inputs": inputs, "roster": roster, "records": {"stage-design:identity:CHR-001:base": record, "prompt-package:avatar:CHR-001:base": {"path": "records/prompt.json", "sha256": prompt_hash, "stale": False, "approval": {"operator": "system:contract-check", "sha256": prompt_hash, "at": "2026-10-22T09:01:00Z"}}}, "images": [image], "reviews": {image["id"]: {"path": "reviews/avatar.json", "sha256": review_hash}}, "references": [], "decisions": [], "pending_impact": None}
    write_json(root / "project.json", state)
    return root / "project.json", state
