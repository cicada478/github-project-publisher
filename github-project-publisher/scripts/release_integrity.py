#!/usr/bin/env python3
"""Verify local SHA-256 values against every uploaded GitHub Release asset."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class AssetResult:
    name: str
    local_digest: str | None
    remote_digest: str | None
    status: str


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def fetch_release(gh: str, repository: str, tag: str) -> dict[str, object]:
    proc = subprocess.run(
        [gh, "api", f"repos/{repository}/releases/tags/{tag}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError("GitHub Release metadata could not be read with gh.")
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("GitHub Release metadata was not valid JSON.") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("GitHub Release metadata had an unexpected shape.")
    return payload


def verify_assets(local_paths: list[Path], release: dict[str, object]) -> list[AssetResult]:
    local_by_name: dict[str, Path] = {}
    for path in local_paths:
        if not path.is_file():
            raise RuntimeError(f"Local asset is not a readable file: {path}")
        if path.name in local_by_name:
            raise RuntimeError(f"Duplicate local asset basename: {path.name}")
        local_by_name[path.name] = path

    raw_assets = release.get("assets", [])
    if not isinstance(raw_assets, list):
        raise RuntimeError("GitHub Release assets had an unexpected shape.")
    remote_by_name: dict[str, str | None] = {}
    for item in raw_assets:
        if not isinstance(item, dict) or not isinstance(item.get("name"), str):
            raise RuntimeError("GitHub Release asset metadata was incomplete.")
        name = item["name"]
        if name in remote_by_name:
            raise RuntimeError(f"Duplicate remote asset name: {name}")
        digest = item.get("digest")
        remote_by_name[name] = digest if isinstance(digest, str) else None

    results: list[AssetResult] = []
    for name in sorted(set(local_by_name) | set(remote_by_name)):
        path = local_by_name.get(name)
        local_digest = sha256(path) if path else None
        remote_digest = remote_by_name.get(name)
        if path is None:
            status = "missing-local"
        elif name not in remote_by_name:
            status = "missing-remote"
        elif remote_digest is None:
            status = "missing-remote-digest"
        elif local_digest != remote_digest.lower():
            status = "mismatch"
        else:
            status = "verified"
        results.append(AssetResult(name, local_digest, remote_digest, status))
    return results


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository", help="GitHub repository as OWNER/REPO")
    parser.add_argument("tag", help="Release Tag")
    parser.add_argument("assets", nargs="*", type=Path, help="Every local file uploaded as a Release asset")
    parser.add_argument("--gh", help="Path to the GitHub CLI executable")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()

    gh = args.gh or shutil.which("gh")
    if not gh:
        print("error: GitHub CLI was not found.", file=sys.stderr)
        return 2
    try:
        release = fetch_release(gh, args.repository, args.tag)
        results = verify_assets([path.resolve() for path in args.assets], release)
    except (OSError, RuntimeError) as exc:
        print(f"error: release asset verification could not complete: {exc}", file=sys.stderr)
        return 2

    status = "not-applicable" if not results else "verified"
    if any(item.status != "verified" for item in results):
        status = "blocked"
    if args.format == "json":
        print(json.dumps({"status": status, "assets": [asdict(item) for item in results]}, indent=2))
    else:
        print(f"Release asset integrity: {status}")
        for item in results:
            print(f"[{item.status.upper()}] {item.name} local={item.local_digest or '-'} remote={item.remote_digest or '-'}")
    return 0 if status in {"verified", "not-applicable"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
