#!/usr/bin/env python3
"""Validate public entrypoints and every vendored child-plugin byte and mode."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re

PUBLIC_SKILLS = ("asset-design", "asset-character", "asset-scene", "asset-prop")
CACHE_PARTS = {"__pycache__", ".pytest_cache", ".cache"}


def cached(path: Path) -> bool:
    return bool(set(path.parts) & CACHE_PARTS) or path.suffix in {".pyc", ".pyo"} or path.name == ".DS_Store"


def validate(root: Path, require_public: bool = True) -> dict:
    root = Path(root).resolve()
    errors = []
    lock = json.loads((root / "bundle-lock.json").read_text(encoding="utf-8"))
    if lock.get("schema_version") != "BundledPluginsLockV1":
        errors.append("Unknown bundle lock schema")
    if lock.get("source_commit") != "c271ae2bfa6665eb4ccdde4565d9cb6a0f2b5fb2":
        errors.append("Unexpected source commit; this release must use the approved ZiChan snapshot")
    if lock.get("source_repository") != "https://github.com/kaibaoxiang-studio/ZiChan":
        errors.append("Unexpected source repository")
    expected_versions = {"character-assets": "0.2.6.4-local", "scene-assets": "0.9.5", "prop-assets": "0.2.5"}
    if set(lock.get("plugins", {})) != set(expected_versions):
        errors.append("Bundle must contain exactly character-assets, scene-assets and prop-assets")
    checked = 0
    for name, entry in lock.get("plugins", {}).items():
        base = root / entry["root"]
        if base != root / "bundled-plugins" / name:
            errors.append(f"Unexpected bundle root: {name}")
            continue
        paths = set()
        for row in entry.get("files", []):
            relative = Path(row["path"])
            if relative.is_absolute() or ".." in relative.parts or relative.as_posix() in paths:
                errors.append(f"Unsafe or duplicate bundle path: {name}/{relative}")
                continue
            paths.add(relative.as_posix())
            target = base / relative
            try:
                data = os.readlink(target).encode() if target.is_symlink() else target.read_bytes()
                if hashlib.sha256(data).hexdigest() != row["sha256"]:
                    errors.append(f"Snapshot hash mismatch: {name}/{relative}")
                mode = "120000" if target.is_symlink() else "100755" if target.stat().st_mode & 0o111 else "100644"
                if mode != row["mode"]:
                    errors.append(f"Snapshot mode mismatch: {name}/{relative}")
                if target.is_symlink() and not target.resolve().is_relative_to(base.resolve()):
                    errors.append(f"Bundle symlink escapes plugin root: {name}/{relative}")
                checked += 1
            except OSError as exc:
                errors.append(f"Unreadable snapshot {name}/{relative}: {exc}")
        actual = {p.relative_to(base).as_posix() for p in base.rglob("*")
                  if (p.is_file() or p.is_symlink()) and not cached(p.relative_to(base))}
        for extra in sorted(actual - paths):
            errors.append(f"Unexpected snapshot file: {name}/{extra}")
        try:
            manifest = json.loads((base / ".codex-plugin/plugin.json").read_text())
            if manifest.get("version") != expected_versions.get(name) or entry.get("version") != manifest.get("version"):
                errors.append(f"Child version mismatch: {name}")
        except (OSError, ValueError) as exc:
            errors.append(f"Unreadable child manifest {name}: {exc}")
    if require_public:
        try:
            manifest = json.loads((root / ".codex-plugin/plugin.json").read_text())
            if manifest.get("name") != "asset-design" or manifest.get("version") != "0.1.0":
                errors.append("Mother plugin must be asset-design v0.1.0")
            if manifest.get("skills") != "./skills/":
                errors.append("Mother manifest must expose only its skills directory")
        except (OSError, ValueError) as exc:
            errors.append(f"Unreadable mother manifest: {exc}")
        found = set()
        for skill in (root / "skills").glob("*/SKILL.md"):
            content = skill.read_text(encoding="utf-8")
            name_match = re.search(r"(?m)^name:\s*[\"']?([^\n\"']+)", content)
            if name_match:
                found.add(name_match.group(1).strip())
            if not content.startswith("---\n") or not re.search(r"(?m)^description:", content):
                errors.append(f"Invalid public skill frontmatter: {skill.parent.name}")
        if found != set(PUBLIC_SKILLS):
            errors.append(f"Expected four public skills, got {sorted(found)}")
        try:
            market = json.loads((root / ".agents/plugins/marketplace.json").read_text())
            if market.get("name") != "asset-design-local" or [p.get("name") for p in market.get("plugins", [])] != ["asset-design"]:
                errors.append("Marketplace must expose asset-design@asset-design-local")
        except (OSError, ValueError) as exc:
            errors.append(f"Unreadable marketplace: {exc}")
    return {"valid": not errors, "checked_bundle_files": checked, "source_commit": lock.get("source_commit"),
            "public_skills": list(PUBLIC_SKILLS) if require_public else [], "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--bundle-only", action="store_true")
    args = parser.parse_args()
    try:
        result = validate(args.root, not args.bundle_only)
    except (OSError, ValueError, KeyError) as exc:
        result = {"valid": False, "errors": [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
