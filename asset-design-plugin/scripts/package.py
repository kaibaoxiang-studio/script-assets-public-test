#!/usr/bin/env python3
"""Build a standalone ZIP with reproducible paths, bytes, permissions and hashes."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_package import cached, validate

EXCLUDED = {".git", ".venv", "venv", "dist", "reports", "outputs", ".runtime", ".runs", ".test-runs"}


def files(root: Path):
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if cached(relative) or set(relative.parts) & EXCLUDED or path.name.endswith((".tmp", ".log")):
            continue
        if path.is_file() or path.is_symlink():
            yield path, relative


def package(root: Path, output: Path, force: bool = False) -> dict:
    root, output = Path(root).resolve(), Path(output).resolve()
    result = validate(root)
    if not result["valid"]:
        raise ValueError("Package validation failed: " + "; ".join(result["errors"]))
    if output.exists() and not force:
        raise ValueError(f"Output already exists; choose another path or use --force: {output}")
    # Exclude any existing output itself even when the output sits outside dist/.
    selected = [(p, rel) for p, rel in files(root) if p != output and p != output.with_suffix(output.suffix + ".sha256")]
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path, relative in selected:
            info = zipfile.ZipInfo("asset-design-plugin/" + relative.as_posix(), date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            mode = stat.S_IFLNK | 0o777 if path.is_symlink() else stat.S_IFREG | (0o755 if path.stat().st_mode & 0o111 else 0o644)
            info.external_attr = mode << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, os.readlink(path).encode() if path.is_symlink() else path.read_bytes())
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    checksum = output.with_suffix(output.suffix + ".sha256")
    checksum.write_text(f"{digest}  {output.name}\n", encoding="utf-8")
    with zipfile.ZipFile(output) as archive:
        corrupt = archive.testzip()
        if corrupt:
            raise ValueError(f"ZIP CRC failure: {corrupt}")
        # Validate a safe temporary extraction through Python's normal modes.
        import tempfile
        with tempfile.TemporaryDirectory(prefix="asset-package-check-") as scratch:
            base = Path(scratch)
            for member in archive.infolist():
                target = base / member.filename
                target.parent.mkdir(parents=True, exist_ok=True)
                mode = member.external_attr >> 16
                data = archive.read(member)
                if stat.S_ISLNK(mode):
                    target.symlink_to(data.decode())
                else:
                    target.write_bytes(data)
                    target.chmod(stat.S_IMODE(mode))
            extracted = validate(base / "asset-design-plugin")
            if not extracted["valid"]:
                raise ValueError("ZIP extracted validation failed: " + "; ".join(extracted["errors"]))
    return {"output": str(output), "sha256": digest, "checksum": str(checksum), "files": len(selected),
            "bytes": output.stat().st_size, "extracted_validation": True}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    try:
        print(json.dumps(package(args.root, args.output, args.force), ensure_ascii=False, indent=2))
    except (ValueError, OSError, zipfile.BadZipFile) as exc:
        parser.exit(2, f"{exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
