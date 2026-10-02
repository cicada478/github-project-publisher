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
OTHER_NOREPLY = "87654321+other-user@users.noreply.github.com"


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
            _, findings = preflight.inspect_repository(root, approved_noreply=NOREPLY)
            identity_codes = {item.code for item in findings if "email" in item.code}
            self.assertEqual(identity_codes, set())

    def test_real_author_and_committer_are_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_repository(root, "developer@example.com")
            _, findings = preflight.inspect_repository(root, approved_noreply=NOREPLY)
            codes = {item.code for item in findings}
            self.assertIn("git-email-not-noreply", codes)
            self.assertIn("commit-author-email-not-approved", codes)
            self.assertIn("commit-committer-email-not-approved", codes)

    def test_explicit_configured_email_is_allowed_with_warning(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_repository(root, "developer@example.com")
            _, findings = preflight.inspect_repository(
                root, identity_policy="configured", approved_noreply=NOREPLY,
            )
            self.assertFalse(any(item.severity == "blocker" and "email" in item.code for item in findings))
            self.assertIn("git-email-public", {item.code for item in findings})

    def test_configured_policy_blocks_a_different_personal_email(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_repository(root, "developer@example.com")
            run_git(root, "config", "user.email", "other@example.com")
            _, findings = preflight.inspect_repository(
                root, identity_policy="configured", approved_noreply=NOREPLY,
            )
            codes = {item.code for item in findings if item.severity == "blocker"}
            self.assertIn("commit-author-email-not-approved", codes)
            self.assertIn("commit-committer-email-not-approved", codes)

    def test_noreply_for_different_account_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_repository(root, OTHER_NOREPLY)
            _, findings = preflight.inspect_repository(root, approved_noreply=NOREPLY)
            codes = {item.code for item in findings if item.severity == "blocker"}
            self.assertIn("git-email-account-mismatch", codes)
            self.assertIn("commit-author-email-not-approved", codes)
            self.assertIn("commit-committer-email-not-approved", codes)

    def test_real_annotated_tag_email_is_a_blocker(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_repository(root, NOREPLY)
            run_git(root, "config", "user.email", "tagger@example.com")
            run_git(root, "tag", "-a", "v1.0.0", "-m", "v1.0.0")
            run_git(root, "config", "user.email", NOREPLY)
            _, findings = preflight.inspect_repository(root, approved_noreply=NOREPLY)
            self.assertIn("tagger-email-not-approved", {item.code for item in findings})

    def test_lightweight_tag_without_tagger_is_not_malformed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_repository(root, NOREPLY)
            run_git(root, "tag", "v1.0.0")
            _, findings = preflight.inspect_repository(root, approved_noreply=NOREPLY)
            self.assertNotIn("git-tag-identity-scan-incomplete", {item.code for item in findings})


class HistoricalContentTests(unittest.TestCase):
    def test_secret_removed_from_worktree_still_blocks_from_history(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_repository(root, NOREPLY)
            synthetic_token = "ghp_" + ("A" * 36)
            (root / "config.txt").write_text(f"token={synthetic_token}\n", encoding="utf-8")
            run_git(root, "add", "--", "config.txt")
            run_git(root, "commit", "-m", "test: add historical fixture")
            (root / "config.txt").write_text("token=REDACTED\n", encoding="utf-8")
            run_git(root, "add", "--", "config.txt")
            run_git(root, "commit", "-m", "test: remove historical fixture")

            metadata, findings = preflight.inspect_repository(root, approved_noreply=NOREPLY)
            history_findings = [item for item in findings if item.code == "history-github-token"]
            self.assertTrue(history_findings)
            self.assertTrue(all((item.path or "").startswith("history:") for item in history_findings))
            self.assertGreater(metadata["historical_text_blob_count"], 0)

    def test_account_resolution_requires_id_and_login_together(self) -> None:
        resolved, error = preflight.resolve_expected_noreply(None, "12345678", None)
        self.assertIsNone(resolved)
        self.assertIsNotNone(error)

    @patch("preflight.shutil.which", return_value="gh")
    @patch("preflight.subprocess.run")
    def test_authenticated_account_resolves_expected_noreply(self, run, _which) -> None:
        run.return_value = subprocess.CompletedProcess([], 0, "12345678\texample-user\n", "")
        resolved, error = preflight.resolve_expected_noreply(None, None, None)
        self.assertEqual(resolved, NOREPLY)
        self.assertIsNone(error)
        self.assertEqual(run.call_args.args[0][1:3], ["api", "user"])


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
