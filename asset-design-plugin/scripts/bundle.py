#!/usr/bin/env python3
"""Copy exact, pinned ZiChan child-plugin Git blobs into this standalone package."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

SOURCE_COMMIT = "b9bb60204d5aaa3b11d998b096dbb7c746b1038f"
SOURCE_REPOSITORY = "https://github.com/kaibaoxiang-studio/ZiChan"
VERSIONS = {"character-assets": "0.2.6.2", "scene-assets": "0.9.5", "prop-assets": "0.2.5"}


def git(repo: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(repo), *args])


def snapshot(repo: Path, root: Path) -> dict:
    commit = git(repo, "rev-parse", f"{SOURCE_COMMIT}^{{commit}}").decode().strip()
    entries = []
    for item in git(repo, "ls-tree", "-rz", commit, *VERSIONS).split(b"\0"):
        if not item:
            continue
        meta, filename = item.split(b"\t", 1)
        mode, kind, blob = meta.decode().split()
        name = filename.decode("utf-8")
        if kind != "blob" or mode not in {"100644", "100755", "120000"}:
            raise ValueError(f"Unsupported Git entry: {name} ({mode} {kind})")
        entries.append((name, mode, blob))
    # Preflight every target so a divergent prior snapshot is never overwritten.
    prepared = []
    for name, mode, blob in entries:
        data = git(repo, "cat-file", "blob", blob)
        target = root / "bundled-plugins" / name
        if target.exists() or target.is_symlink():
            existing = os.readlink(target).encode() if target.is_symlink() else target.read_bytes()
            if existing != data or (target.is_symlink() != (mode == "120000")):
                raise ValueError(f"Refusing to overwrite divergent snapshot: {target}")
        prepared.append((name, mode, blob, data, target))
    lock = {"schema_version": "BundledPluginsLockV1", "source_repository": SOURCE_REPOSITORY,
            "source_commit": commit, "plugins": {}}
    for plugin, version in VERSIONS.items():
        manifest_data = git(repo, "show", f"{commit}:{plugin}/.codex-plugin/plugin.json")
        if json.loads(manifest_data)["version"] != version:
            raise ValueError(f"Pinned version does not match source manifest: {plugin}")
        lock["plugins"][plugin] = {"version": version, "root": f"bundled-plugins/{plugin}", "files": []}
    for name, mode, blob, data, target in prepared:
        plugin, relative = name.split("/", 1)
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists() and not target.is_symlink():
            if mode == "120000":
                target.symlink_to(data.decode())
            else:
                target.write_bytes(data)
        if mode != "120000":
            target.chmod(0o755 if mode == "100755" else 0o644)
        lock["plugins"][plugin]["files"].append({"path": relative, "mode": mode,
            "git_blob": blob, "sha256": hashlib.sha256(data).hexdigest()})
    text = json.dumps(lock, ensure_ascii=False, indent=2) + "\n"
    lockfile = root / "bundle-lock.json"
    if lockfile.exists() and lockfile.read_text() != text:
        raise ValueError("Existing bundle-lock.json differs; use an explicit upgrade workflow")
    lockfile.write_text(text, encoding="utf-8")
    return {"source_commit": commit, "plugins": {k: {"version": v["version"], "files": len(v["files"])}
            for k, v in lock["plugins"].items()}, "lock_sha256": hashlib.sha256(text.encode()).hexdigest()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-repo", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        print(json.dumps(snapshot(args.source_repo.resolve(), args.root.resolve()), ensure_ascii=False, indent=2))
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        parser.exit(2, f"{exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
