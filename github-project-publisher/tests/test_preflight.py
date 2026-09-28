from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import preflight  # noqa: E402
import release_integrity  # noqa: E402


NOREPLY = "12345678+example-user@users.noreply.github.com"


def run_git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True)


def make_repository(root: Path, email: str) -> None:
    run_git(root, "init", "--initial-branch=main")
    run_git(root, "config", "user.name", "Example User")
    run_git(root, "config", "user.email", email)
    (root / "README.md").write_text("# Example\n", encoding="utf-8")
    (root / ".gitignore").write_text("*.tmp\n", encoding="utf-8")
    (root / "LICENSE").write_text("Example license\n", encoding="utf-8")
    run_git(root, "add", "--", "README.md", ".gitignore", "LICENSE")
    run_git(root, "commit", "-m", "chore: initialize example")
    run_git(root, "remote", "add", "origin", "https://github.com/example/project.git")


class PreflightIdentityTests(unittest.TestCase):
    def test_id_noreply_history_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_repository(root, NOREPLY)
            _, findings = preflight.inspect_repository(root)
            identity_codes = {item.code for item in findings if "email" in item.code}
            self.assertEqual(identity_codes, set())

    def test_real_author_and_committer_are_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_repository(root, "developer@example.com")
            _, findings = preflight.inspect_repository(root)
            codes = {item.code for item in findings}
            self.assertIn("git-email-not-noreply", codes)
            self.assertIn("commit-author-email-not-noreply", codes)
            self.assertIn("commit-committer-email-not-noreply", codes)

    def test_real_annotated_tag_email_is_a_blocker(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_repository(root, NOREPLY)
            run_git(root, "config", "user.email", "tagger@example.com")
            run_git(root, "tag", "-a", "v1.0.0", "-m", "v1.0.0")
            run_git(root, "config", "user.email", NOREPLY)
            _, findings = preflight.inspect_repository(root)
            self.assertIn("tagger-email-not-noreply", {item.code for item in findings})


class ReleaseIntegrityTests(unittest.TestCase):
    @patch("release_integrity.subprocess.run")
    def test_draft_release_falls_back_to_paginated_list(self, run) -> None:
        run.side_effect = [
            subprocess.CompletedProcess([], 1, "", "not found"),
            subprocess.CompletedProcess(
                [], 0, '[[{"tag_name":"v0.2.0","assets":[]}]]', ""
            ),
        ]
        release = release_integrity.fetch_release("gh", "example/project", "v0.2.0")
        self.assertEqual(release["tag_name"], "v0.2.0")
        self.assertIn("--paginate", run.call_args_list[1].args[0])

    def test_matching_asset_digest_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            asset = Path(directory) / "artifact.zip"
            asset.write_bytes(b"verified artifact")
            digest = "sha256:" + hashlib.sha256(asset.read_bytes()).hexdigest()
            results = release_integrity.verify_assets([asset], {"assets": [{"name": asset.name, "digest": digest}]})
            self.assertEqual([item.status for item in results], ["verified"])

    def test_remote_asset_without_local_file_blocks(self) -> None:
        results = release_integrity.verify_assets([], {"assets": [{"name": "missing.zip", "digest": "sha256:00"}]})
        self.assertEqual([item.status for item in results], ["missing-local"])

    def test_no_assets_is_not_applicable(self) -> None:
        self.assertEqual(release_integrity.verify_assets([], {"assets": []}), [])


if __name__ == "__main__":
    unittest.main()
