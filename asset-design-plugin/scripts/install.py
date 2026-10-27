#!/usr/bin/env python3
"""Install this validated package using the supported Codex plugin CLI."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_package import validate


def install(root: Path, codex_bin: str = "codex", dry_run: bool = False) -> dict:
    root = Path(root).resolve()
    report = validate(root)
    if not report["valid"]:
        raise ValueError("Cannot install invalid package: " + "; ".join(report["errors"]))
    executable = shutil.which(codex_bin)
    if not executable:
        raise ValueError("Codex CLI not found; pass --codex-bin with its executable path")
    commands = [[executable, "plugin", "marketplace", "add", str(root), "--json"],
                [executable, "plugin", "add", "asset-design@asset-design-local", "--json"]]
    results = []
    if not dry_run:
        for command in commands:
            completed = subprocess.run(command, capture_output=True, text=True)
            if completed.returncode:
                raise ValueError(f"Codex plugin command failed ({completed.returncode}): {completed.stderr.strip() or completed.stdout.strip()}")
            try:
                response = json.loads(completed.stdout)
            except ValueError:
                response = {"output": completed.stdout.strip()}
            results.append(response)
    return {"installed": not dry_run, "dry_run": dry_run, "plugin": "asset-design@asset-design-local",
            "commands": commands, "results": results,
            "note": "Open a new chat to refresh the installed skill list."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        print(json.dumps(install(args.root, args.codex_bin, args.dry_run), ensure_ascii=False, indent=2))
    except (ValueError, OSError) as exc:
        parser.exit(2, f"{exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
