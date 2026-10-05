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


class MachineLocalPathTests(unittest.TestCase):
    def scan(self, text: str, suffix: str = ".py", prefix: str = "") -> list:
        findings: list = []
        preflight.scan_text_lines(text.splitlines(), "candidate" + suffix, suffix, findings, prefix)
        return [item for item in findings if item.code.endswith("machine-local-path")]

    def test_runtime_and_personal_paths_are_redacted_warnings(self) -> None:
        cases = [
            (r'python = "C:\Users\ActualPerson\miniconda3\python.exe"', ".py"),
            (r'{"python": "C:\\Users\\ActualPerson\\python.exe"}', ".json"),
            ('setwd("D:/research/data")', ".R"),
            ('R = "C:/Program Files/R/R-4.4.0/bin/Rscript.exe"', ".toml"),
            ('python = "/home/actualperson/venv/bin/python"', ".sh"),
            ('data = "/Users/实际用户/private/data.csv"', ".R"),
            ('R = "/opt/R/4.4/bin/Rscript"', ".yaml"),
            ('python = "/usr/local/bin/python3.12"', ".sh"),
        ]
        for text, suffix in cases:
            with self.subTest(text=text):
                findings = self.scan("# header\n" + text, suffix)
                self.assertEqual(len(findings), 1)
                self.assertEqual(findings[0].severity, "warning")
                self.assertEqual(findings[0].line, 2)
                self.assertNotIn("ActualPerson", findings[0].message)
                self.assertNotIn(text, findings[0].message)

    def test_portable_paths_and_documented_placeholders_are_quiet(self) -> None:
        for text in [
            '#!/usr/bin/env python3', 'root = "/app/data"',
            'python = sys.executable', 'data = "./data/input.csv"',
            'python = "$HOME/.venv/bin/python"',
            'https://example.org/home/user/data',
        ]:
            with self.subTest(text=text):
                self.assertEqual(self.scan(text), [])
        for text in [r'C:\path\to\python.exe', r'C:\Users\username\project', '/home/example-user/project']:
            with self.subTest(text=text):
                self.assertEqual(self.scan(text, ".md"), [])
        self.assertEqual(len(self.scan(r'C:\Users\username\project')), 1)

    def test_history_paths_are_advisory_without_weakening_secret_checks(self) -> None:
        findings = self.scan('root = "/home/actualperson/project"', prefix="history-")
        self.assertEqual(findings[0].severity, "advisory")
        self.assertEqual(findings[0].code, "history-machine-local-path")
        all_findings: list = []
        preflight.scan_text_lines(
            ['root = "/home/actualperson/project"', '-----BEGIN PRIVATE KEY-----'],
            "history:example:task.py", ".py", all_findings, "history-",
        )
        self.assertTrue(any(item.code == "history-private-key" and item.severity == "blocker" for item in all_findings))

    def test_r_worktree_and_removed_historical_path_are_scanned(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_repository(root, NOREPLY)
            script = root / "analysis.R"
            script.write_text('setwd("D:/research/data")\n', encoding="utf-8")
            _, findings = preflight.inspect_repository(root)
            self.assertTrue(any(item.code == "machine-local-path" and item.path == "analysis.R" for item in findings))
            run_git(root, "add", "--", "analysis.R")
            run_git(root, "commit", "-m", "test: local path fixture")
            script.write_text('data <- "./data"\n', encoding="utf-8")
            run_git(root, "add", "--", "analysis.R")
            run_git(root, "commit", "-m", "test: portable path fixture")
            _, findings = preflight.inspect_repository(root, include_worktree=False, requested_refs=["main"])
            path_findings = [item for item in findings if item.code.endswith("machine-local-path")]
            self.assertEqual(len(path_findings), 1)
            self.assertEqual(path_findings[0].severity, "advisory")
            self.assertNotIn("D:/research/data", repr(path_findings))


class PreflightIdentityTests(unittest.TestCase):
    def test_id_noreply_history_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_repository(root, NOREPLY)
            _, findings = preflight.inspect_repository(root, approved_noreply=NOREPLY)
            identity_codes = {item.code for item in findings if "email" in item.code}
            self.assertEqual(identity_codes, set())

    def test_existing_personal_identity_is_reported_without_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_repository(root, "developer@example.com")
            _, findings = preflight.inspect_repository(root, approved_noreply=NOREPLY)
            codes = {item.code for item in findings}
            self.assertIn("git-email-public", codes)
            self.assertIn("commit-author-email-outside-current-policy", codes)
            self.assertIn("commit-committer-email-outside-current-policy", codes)
            self.assertFalse(any(item.severity == "blocker" and "email" in item.code for item in findings))

    def test_explicit_configured_email_is_allowed_with_warning(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_repository(root, "developer@example.com")
            _, findings = preflight.inspect_repository(
                root, identity_policy="configured", approved_noreply=NOREPLY,
            )
            self.assertFalse(any(item.severity == "blocker" and "email" in item.code for item in findings))
            self.assertIn("git-email-public", {item.code for item in findings})

    def test_configured_policy_allows_collaborative_history_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_repository(root, "developer@example.com")
            run_git(root, "config", "user.email", "other@example.com")
            _, findings = preflight.inspect_repository(
                root, identity_policy="configured", approved_noreply=NOREPLY,
            )
            codes = {item.code for item in findings}
            self.assertIn("commit-author-email-outside-current-policy", codes)
            self.assertIn("commit-committer-email-outside-current-policy", codes)
            self.assertFalse(any(item.severity == "blocker" and "email" in item.code for item in findings))

    def test_strict_history_identity_policy_blocks_mismatches(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_repository(root, "developer@example.com")
            run_git(root, "config", "user.email", NOREPLY)
            _, findings = preflight.inspect_repository(
                root,
                identity_policy="noreply",
                history_identity_policy="strict",
                approved_noreply=NOREPLY,
            )
            blockers = {item.code for item in findings if item.severity == "blocker"}
            self.assertIn("commit-author-email-outside-current-policy", blockers)
            self.assertIn("commit-committer-email-outside-current-policy", blockers)

    def test_noreply_for_different_account_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_repository(root, OTHER_NOREPLY)
            _, findings = preflight.inspect_repository(
                root, approved_noreply=NOREPLY, requested_refs=["v1.0.0"],
            )
            codes = {item.code for item in findings if item.severity == "blocker"}
            self.assertNotIn("git-email-account-mismatch", codes)

            _, publish_findings = preflight.inspect_repository(
                root, identity_policy="noreply", approved_noreply=NOREPLY,
            )
            publish_codes = {item.code for item in publish_findings if item.severity == "blocker"}
            self.assertIn("git-email-account-mismatch", publish_codes)

    def test_existing_annotated_tag_identity_is_advisory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_repository(root, NOREPLY)
            run_git(root, "config", "user.email", "tagger@example.com")
            run_git(root, "tag", "-a", "v1.0.0", "-m", "v1.0.0")
            run_git(root, "config", "user.email", NOREPLY)
            _, findings = preflight.inspect_repository(
                root, approved_noreply=NOREPLY, requested_refs=["v1.0.0"],
            )
            matches = [item for item in findings if item.code == "tagger-email-outside-current-policy"]
            self.assertTrue(matches)
            self.assertTrue(all(item.severity == "advisory" for item in matches))

    def test_lightweight_tag_without_tagger_is_not_malformed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_repository(root, NOREPLY)
            run_git(root, "tag", "v1.0.0")
            _, findings = preflight.inspect_repository(
                root, approved_noreply=NOREPLY, requested_refs=["v1.0.0"],
            )
            self.assertNotIn("git-tag-identity-scan-incomplete", {item.code for item in findings})


class HistoricalContentTests(unittest.TestCase):
    def test_empty_repository_can_be_audited_before_first_commit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run_git(root, "init", "--initial-branch=main")
            (root / "README.md").write_text("# Empty repository\n", encoding="utf-8")
            metadata, findings = preflight.inspect_repository(root)
            self.assertEqual(metadata["publication_refs"], [])
            self.assertNotIn("git-identity-scan-failed", {item.code for item in findings})
            self.assertNotIn("history-content-scan-failed", {item.code for item in findings})

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

    def test_unchanged_tip_blob_is_not_scanned_twice(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_repository(root, NOREPLY)
            synthetic_token = "ghp_" + ("D" * 36)
            (root / "current.txt").write_text(f"token={synthetic_token}\n", encoding="utf-8")
            run_git(root, "add", "--", "current.txt")
            run_git(root, "commit", "-m", "test: add current fixture")

            metadata, findings = preflight.inspect_repository(root, approved_noreply=NOREPLY)
            self.assertIn("github-token", {item.code for item in findings})
            self.assertNotIn("history-github-token", {item.code for item in findings})
            self.assertGreater(metadata["deduplicated_history_blob_count"], 0)

    def test_modified_worktree_does_not_hide_secret_in_tip_history(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_repository(root, NOREPLY)
            synthetic_token = "ghp_" + ("E" * 36)
            (root / "current.txt").write_text(f"token={synthetic_token}\n", encoding="utf-8")
            run_git(root, "add", "--", "current.txt")
            run_git(root, "commit", "-m", "test: add current fixture")
            (root / "current.txt").write_text("token=REDACTED\n", encoding="utf-8")

            _, findings = preflight.inspect_repository(root, approved_noreply=NOREPLY)
            self.assertIn("history-github-token", {item.code for item in findings})

    def test_unpublished_branch_is_outside_default_head_scan(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_repository(root, NOREPLY)
            run_git(root, "switch", "-c", "private-experiment")
            synthetic_token = "ghp_" + ("B" * 36)
            (root / "experiment.txt").write_text(f"token={synthetic_token}\n", encoding="utf-8")
            run_git(root, "add", "--", "experiment.txt")
            run_git(root, "commit", "-m", "test: add branch-only fixture")
            run_git(root, "switch", "main")

            _, default_findings = preflight.inspect_repository(root, approved_noreply=NOREPLY)
            self.assertNotIn("history-github-token", {item.code for item in default_findings})

            _, branch_findings = preflight.inspect_repository(
                root, approved_noreply=NOREPLY, requested_refs=["private-experiment"],
            )
            self.assertIn("history-github-token", {item.code for item in branch_findings})

    def test_committed_only_ignores_unrelated_untracked_secret(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_repository(root, NOREPLY)
            synthetic_token = "ghp_" + ("C" * 36)
            (root / "local-notes.txt").write_text(f"token={synthetic_token}\n", encoding="utf-8")

            _, worktree_findings = preflight.inspect_repository(root, approved_noreply=NOREPLY)
            self.assertIn("github-token", {item.code for item in worktree_findings})

            metadata, committed_findings = preflight.inspect_repository(
                root, approved_noreply=NOREPLY, include_worktree=False,
            )
            self.assertNotIn("github-token", {item.code for item in committed_findings})
            self.assertFalse(metadata["worktree_content_scanned"])

    def test_large_extensionless_text_history_is_not_silently_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_repository(root, NOREPLY)
            (root / "payload").write_text("plain text larger than test limit\n", encoding="utf-8")
            run_git(root, "add", "--", "payload")
            run_git(root, "commit", "-m", "test: add extensionless text")
            (root / "payload").unlink()
            run_git(root, "add", "--", "payload")
            run_git(root, "commit", "-m", "test: remove extensionless text")

            with patch.object(preflight, "MAX_TEXT_SCAN_BYTES", 8):
                _, findings = preflight.inspect_repository(root, approved_noreply=NOREPLY)
            self.assertIn("history-content-scan-incomplete", {item.code for item in findings})

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
