#!/usr/bin/env python3
"""Conservative, read-only GitHub publication preflight for local repositories."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    path: str | None = None
    line: int | None = None


SKIP_DIRS = {".git", ".hg", ".svn", "node_modules", ".venv", "venv", "__pycache__"}
SENSITIVE_NAMES = {
    ".env", ".env.local", ".npmrc", ".pypirc", "credentials.json",
    "service-account.json", "secrets.json", "secrets.yaml", "secrets.yml",
    ".htpasswd", "kubeconfig", "wallet.dat", "id_rsa", "id_ed25519",
}
GENERATED_DIRS = {
    ".cache", ".idea", ".pytest_cache", ".vscode", "coverage", "dist", "build", "target",
}
TEMP_SUFFIXES = {".bak", ".swp", ".temp", ".tmp"}
LOG_DIRS = {"log", "logs", "debug", "dumps", "crash", "crashes", "diagnostics"}
LOG_SUFFIXES = {".log", ".trace", ".dump", ".har"}
TEXT_EXTENSIONS = {
    ".c", ".cc", ".cfg", ".conf", ".cpp", ".cs", ".css", ".csv", ".go",
    ".h", ".hpp", ".html", ".ini", ".java", ".js", ".json", ".jsx", ".kt",
    ".md", ".mjs", ".php", ".properties", ".ps1", ".py", ".rb", ".rs", ".sh",
    ".sql", ".toml", ".ts", ".tsx", ".txt", ".xml", ".yaml", ".yml",
}
SOURCE_EXTENSIONS = {".c", ".cc", ".cpp", ".cs", ".go", ".java", ".js", ".jsx", ".kt", ".php", ".py", ".rb", ".rs", ".ts", ".tsx"}
SECRET_PATTERNS = (
    ("private-key", re.compile(r"^\s*-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----\s*$")),
    ("github-token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{60,})\b")),
    ("aws-access-key", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("stripe-live-key", re.compile(r"\b(?:sk|rk)_live_[0-9A-Za-z]{16,}\b")),
    ("slack-webhook", re.compile(r"https://hooks\.slack\.com/services/[A-Za-z0-9/_-]{20,}")),
    ("credential-in-url", re.compile(
        r"(?i)\b(?:https?|postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis)://[^\s/:@]+:[^\s/@]+@"
    )),
    ("authorization-value", re.compile(
        r"(?i)\b(?:authorization|proxy-authorization)\b\s*[:=]\s*(?:basic|bearer)\s+[A-Za-z0-9._~+/=-]{12,}"
    )),
    ("session-or-cookie", re.compile(
        r"(?i)\b(?:set-cookie|cookie|session[_-]?id|refresh[_-]?token)\b\s*[:=]\s*[\"']?[^\s;\"']{12,}"
    )),
    ("secret-in-query", re.compile(
        r"(?i)[?&](?:api[_-]?key|access[_-]?token|auth[_-]?token|password|secret)=[A-Za-z0-9%._~+/=-]{12,}"
    )),
    ("generic-secret-assignment", re.compile(
        r"(?i)\b(?:api[_-]?key|client[_-]?secret|access[_-]?token|auth[_-]?token|password|passwd|pwd)\b\s*[:=]\s*[\"']?[A-Za-z0-9+/=._~-]{8,}"
    )),
)
EMAIL_PATTERN = re.compile(r"(?<![\w.+-])[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}(?![\w.-])", re.IGNORECASE)
ID_NOREPLY_PATTERN = re.compile(r"^[0-9]+\+[A-Z0-9-]+@users\.noreply\.github\.com$", re.IGNORECASE)
PHONE_CONTEXT_PATTERN = re.compile(
    r"(?i)(?:phone|mobile|telephone|tel|手机号|手机|电话)\s*[:=：]\s*\+?[0-9][0-9() .-]{6,18}[0-9]"
)
ADDRESS_CONTEXT_PATTERN = re.compile(
    r"(?i)(?:home[_ -]?address|billing[_ -]?address|shipping[_ -]?address|住址|家庭地址|账单地址|收货地址)\s*[:=：]\s*\S.{5,}"
)
SSN_CONTEXT_PATTERN = re.compile(r"(?i)(?:ssn|social security(?: number)?)\s*[:=]\s*\d{3}-?\d{2}-?\d{4}")
CVV_CONTEXT_PATTERN = re.compile(r"(?i)(?:cvv|cvc|card[_ -]?security[_ -]?code|安全码)\s*[:=：]\s*\d{3,4}\b")
CHINA_ID_PATTERN = re.compile(r"(?<!\d)(\d{17}[0-9Xx])(?!\d)")
CARD_PATTERN = re.compile(r"(?<!\d)(?:\d[ -]?){12,18}\d(?!\d)")
IBAN_PATTERN = re.compile(r"(?<![A-Z0-9])([A-Z]{2}\d{2}(?:[ ]?[A-Z0-9]){11,30})(?![A-Z0-9])", re.IGNORECASE)
SENSITIVE_LOG_SINK_PATTERN = re.compile(
    r"(?i)\b(?:console\.(?:log|debug|info|warn|error)|(?:log|logger)\.(?:trace|debug|info|warn|warning|error|critical|exception)|print)\s*\([^\n]*(?:api[_-]?key|password|passwd|access[_-]?token|auth(?:orization)?|cookie|session|private[_-]?key|card[_ -]?number|cvv|cvc|身份证|手机号)"
)
MAX_TEXT_SCAN_BYTES = 25 * 1024 * 1024


def git(root: Path, *args: str) -> tuple[int, str]:
    proc = subprocess.run(
        ["git", "-C", str(root), *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8", errors="replace", check=False,
    )
    return proc.returncode, proc.stdout.strip()


def is_id_noreply(value: str) -> bool:
    return bool(ID_NOREPLY_PATTERN.fullmatch(value.strip().strip("<>")))


def normalized_email(value: str) -> str:
    return value.strip().strip("<>").casefold()


def expected_noreply(github_id: str, github_login: str) -> str:
    if not github_id.isdigit() or not re.fullmatch(r"[A-Za-z0-9-]+", github_login):
        raise ValueError("GitHub account identity had an invalid ID or login shape.")
    return f"{github_id}+{github_login}@users.noreply.github.com"


def resolve_expected_noreply(
    gh_option: str | None,
    github_id: str | None,
    github_login: str | None,
) -> tuple[str | None, str | None]:
    if bool(github_id) != bool(github_login):
        return None, "Both --expected-github-id and --expected-github-login are required together."
    if github_id and github_login:
        try:
            return expected_noreply(github_id, github_login), None
        except ValueError as exc:
            return None, str(exc)

    gh = gh_option or shutil.which("gh")
    if not gh:
        return None, "GitHub CLI was not found; authenticated account ownership could not be verified."
    proc = subprocess.run(
        [gh, "api", "user", "--jq", "[.id,.login] | @tsv"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if proc.returncode != 0:
        return None, "The authenticated GitHub account could not be resolved with gh."
    parts = proc.stdout.strip().split("\t")
    if len(parts) != 2:
        return None, "GitHub account metadata had an unexpected shape."
    try:
        return expected_noreply(parts[0], parts[1]), None
    except ValueError as exc:
        return None, str(exc)


def is_approved_email(
    value: str,
    configured_email: str,
    identity_policy: str,
    approved_noreply: str | None,
) -> bool:
    if is_id_noreply(value):
        return approved_noreply is None or normalized_email(value) == normalized_email(approved_noreply)
    return (
        identity_policy == "configured"
        and bool(configured_email)
        and normalized_email(value) == normalized_email(configured_email)
    )


def scan_git_identities(
    root: Path,
    findings: list[Finding],
    metadata: dict[str, object],
    identity_policy: str,
    approved_noreply: str | None,
    account_error: str | None,
) -> None:
    code, configured_email = git(root, "config", "--local", "--get", "user.email")
    metadata["identity_policy"] = identity_policy
    metadata["github_account_verified"] = approved_noreply is not None
    if approved_noreply is None:
        findings.append(Finding(
            "blocker", "github-account-unverified",
            account_error or "Authenticated GitHub account ownership could not be verified.",
            "github-account",
        ))
    metadata["local_noreply_configured"] = code == 0 and is_id_noreply(configured_email)
    if code != 0 or not configured_email:
        findings.append(Finding(
            "blocker", "git-email-not-configured",
            "Repository-local Git email is missing; configure the explicitly selected publication identity.",
            "git-config:user.email",
        ))
    elif identity_policy == "noreply" and not is_id_noreply(configured_email):
        findings.append(Finding(
            "blocker", "git-email-not-noreply",
            "Repository-local Git email is not an ID-based GitHub noreply address; value intentionally redacted.",
            "git-config:user.email",
        ))
    elif is_id_noreply(configured_email) and approved_noreply and normalized_email(configured_email) != normalized_email(approved_noreply):
        findings.append(Finding(
            "blocker", "git-email-account-mismatch",
            "Repository-local noreply email does not belong to the authenticated GitHub account; value intentionally redacted.",
            "git-config:user.email",
        ))
    elif identity_policy == "configured" and not is_id_noreply(configured_email):
        findings.append(Finding(
            "warning", "git-email-public",
            "The selected repository-local Git email will be public in Git metadata; value intentionally redacted.",
            "git-config:user.email",
        ))

    code, history = git(root, "log", "--all", "--format=%H%x09%ae%x09%ce")
    if code != 0:
        findings.append(Finding("blocker", "git-identity-scan-failed", "Commit identity metadata could not be inspected."))
    commit_count = 0
    if code == 0:
        for row in history.splitlines():
            if not row:
                continue
            parts = row.split("\t")
            if len(parts) != 3:
                findings.append(Finding("blocker", "git-identity-scan-incomplete", "Unexpected commit identity metadata format."))
                continue
            commit_count += 1
            sha, author_email, committer_email = parts
            if not is_approved_email(author_email, configured_email, identity_policy, approved_noreply):
                findings.append(Finding(
                    "blocker", "commit-author-email-not-approved",
                    "Commit Author email is not approved by the selected identity policy; value intentionally redacted.",
                    f"commit:{sha}",
                ))
            if not is_approved_email(committer_email, configured_email, identity_policy, approved_noreply):
                findings.append(Finding(
                    "blocker", "commit-committer-email-not-approved",
                    "Commit Committer email is not approved by the selected identity policy; value intentionally redacted.",
                    f"commit:{sha}",
                ))
    metadata["commit_identity_count"] = commit_count

    code, tags = git(
        root, "for-each-ref", "--format=%(refname)%09%(objecttype)%09%(taggeremail)", "refs/tags",
    )
    if code != 0:
        findings.append(Finding("blocker", "git-tag-identity-scan-failed", "Tag identity metadata could not be inspected."))
        return
    annotated_count = 0
    for row in tags.splitlines():
        if not row:
            continue
        parts = row.split("\t")
        # GitHub Actions can materialize the checked-out tag ref as a
        # lightweight ref to the workflow's commit. Because git() removes
        # trailing whitespace, its empty tagger field leaves two columns.
        # Lightweight tags have no Tagger identity to validate.
        if len(parts) == 2 and parts[1] != "tag":
            continue
        if len(parts) != 3:
            findings.append(Finding("blocker", "git-tag-identity-scan-incomplete", "Unexpected Tag identity metadata format."))
            continue
        refname, object_type, tagger_email = parts
        if object_type != "tag":
            continue
        annotated_count += 1
        if not is_approved_email(tagger_email, configured_email, identity_policy, approved_noreply):
            findings.append(Finding(
                "blocker", "tagger-email-not-approved",
                "Annotated Tag tagger email is not approved by the selected identity policy; value intentionally redacted.",
                refname,
            ))
    metadata["annotated_tag_identity_count"] = annotated_count


def candidate_files(root: Path, is_git: bool) -> list[Path]:
    if is_git:
        code, output = git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z")
        if code == 0:
            return [root / item for item in output.split("\0") if item]
        raise RuntimeError("git ls-files failed; the publication set could not be enumerated")
    files: list[Path] = []
    for current, dirs, names in os.walk(root):
        dirs[:] = [name for name in dirs if name not in SKIP_DIRS]
        files.extend(Path(current) / name for name in names)
    return files


def is_probably_text(path: Path) -> bool:
    if path.suffix.lower() in TEXT_EXTENSIONS or path.name.lower() in {
        "dockerfile", "makefile", "readme", "license", "notice",
    }:
        return True
    try:
        with path.open("rb") as handle:
            return b"\0" not in handle.read(4096)
    except OSError:
        return False


def relative(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def is_log_path(relative_path: Path) -> bool:
    name = relative_path.name.lower()
    suffixes = [suffix.lower() for suffix in relative_path.suffixes]
    parts = {part.lower() for part in relative_path.parts[:-1]}
    return bool(parts & LOG_DIRS) or any(suffix in LOG_SUFFIXES for suffix in suffixes) or ".log." in name


def valid_luhn(number: str) -> bool:
    digits = [int(char) for char in number if char.isdigit()]
    if not 13 <= len(digits) <= 19 or len(set(digits)) == 1:
        return False
    total = 0
    parity = len(digits) % 2
    for index, digit in enumerate(digits):
        if index % 2 == parity:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0


def valid_china_id(value: str) -> bool:
    if len(value) != 18 or not value[:17].isdigit():
        return False
    weights = (7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2)
    checks = "10X98765432"
    return checks[sum(int(digit) * weight for digit, weight in zip(value[:17], weights)) % 11] == value[-1].upper()


def valid_iban(value: str) -> bool:
    compact = re.sub(r"\s+", "", value).upper()
    if not 15 <= len(compact) <= 34 or not re.fullmatch(r"[A-Z]{2}\d{2}[A-Z0-9]+", compact):
        return False
    rearranged = compact[4:] + compact[:4]
    remainder = 0
    for char in rearranged:
        expanded = char if char.isdigit() else str(ord(char) - 55)
        for digit in expanded:
            remainder = (remainder * 10 + int(digit)) % 97
    return remainder == 1


def add_redacted_finding(findings: list[Finding], code: str, rel: str, line: int) -> None:
    findings.append(Finding(
        "blocker", code, "Potential sensitive or private data detected; value intentionally redacted.", rel, line,
    ))


def scan_text_lines(
    lines: Iterable[str],
    rel: str,
    suffix: str,
    findings: list[Finding],
    code_prefix: str = "",
) -> None:
    relative_path = Path(rel)
    log_file = is_log_path(relative_path)
    source_file = suffix.lower() in SOURCE_EXTENSIONS
    for number, line in enumerate(lines, 1):
        for code, pattern in SECRET_PATTERNS:
            if pattern.search(line):
                add_redacted_finding(findings, f"{code_prefix}{code}", rel, number)

        if any(valid_china_id(match.group(1)) for match in CHINA_ID_PATTERN.finditer(line)):
            add_redacted_finding(findings, f"{code_prefix}personal-id-number", rel, number)
        if any(valid_luhn(match.group(0)) for match in CARD_PATTERN.finditer(line)):
            add_redacted_finding(findings, f"{code_prefix}payment-card-number", rel, number)
        if any(valid_iban(match.group(1)) for match in IBAN_PATTERN.finditer(line)):
            add_redacted_finding(findings, f"{code_prefix}bank-account-identifier", rel, number)
        if CVV_CONTEXT_PATTERN.search(line):
            add_redacted_finding(findings, f"{code_prefix}payment-security-code", rel, number)
        if source_file and SENSITIVE_LOG_SINK_PATTERN.search(line):
            add_redacted_finding(findings, f"{code_prefix}sensitive-data-log-sink", rel, number)

        if log_file:
            if EMAIL_PATTERN.search(line):
                add_redacted_finding(findings, f"{code_prefix}log-personal-email", rel, number)
            if PHONE_CONTEXT_PATTERN.search(line):
                add_redacted_finding(findings, f"{code_prefix}log-personal-phone", rel, number)
            if ADDRESS_CONTEXT_PATTERN.search(line):
                add_redacted_finding(findings, f"{code_prefix}log-personal-address", rel, number)
            if SSN_CONTEXT_PATTERN.search(line):
                add_redacted_finding(findings, f"{code_prefix}log-personal-id", rel, number)


def current_tracked_blobs(root: Path) -> dict[str, str]:
    code, output = git(root, "ls-files", "--stage", "-z")
    if code != 0:
        raise RuntimeError("git ls-files failed; current tracked blobs could not be identified")
    result: dict[str, str] = {}
    for row in output.split("\0"):
        if not row or "\t" not in row:
            continue
        metadata, path = row.split("\t", 1)
        parts = metadata.split()
        if len(parts) >= 3 and parts[2] == "0":
            result[path.replace("\\", "/")] = parts[1]
    return result


def history_blob_entries(root: Path) -> list[tuple[str, str, int]]:
    code, output = git(root, "rev-list", "--objects", "--all")
    if code != 0:
        raise RuntimeError("git rev-list failed; historical objects could not be enumerated")
    objects: list[tuple[str, str]] = []
    for row in output.splitlines():
        sha, separator, path = row.partition(" ")
        if sha:
            objects.append((sha, path.replace("\\", "/") if separator else ""))
    if not objects:
        return []
    proc = subprocess.run(
        ["git", "-C", str(root), "cat-file", "--batch-check=%(objectname) %(objecttype) %(objectsize)"],
        input="\n".join(sha for sha, _ in objects) + "\n",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError("git cat-file failed; historical objects could not be classified")
    classifications = proc.stdout.splitlines()
    if len(classifications) != len(objects):
        raise RuntimeError("historical object classification was incomplete")
    entries: list[tuple[str, str, int]] = []
    seen: set[str] = set()
    for (requested_sha, path), row in zip(objects, classifications):
        parts = row.split()
        if len(parts) != 3 or parts[1] != "blob" or requested_sha in seen:
            continue
        try:
            size = int(parts[2])
        except ValueError as exc:
            raise RuntimeError("historical blob size was invalid") from exc
        seen.add(requested_sha)
        entries.append((requested_sha, path, size))
    return entries


def scan_history_content(root: Path, findings: list[Finding], metadata: dict[str, object]) -> None:
    current = current_tracked_blobs(root)
    entries = history_blob_entries(root)
    scanned = 0
    for sha, path_text, size in entries:
        if path_text and current.get(path_text) == sha:
            continue
        display_path = path_text or "<pathless-blob>"
        historical_location = f"history:{sha[:12]}:{display_path}"
        path = Path(display_path)
        lower_name = path.name.lower()
        if lower_name in SENSITIVE_NAMES or lower_name.startswith(".env.") or path.suffix.lower() in {".key", ".p12", ".pfx", ".pem", ".jks", ".keystore", ".ovpn"}:
            findings.append(Finding(
                "blocker", "history-sensitive-filename",
                "Potential credential or private-key file exists in reachable Git history; inspect without disclosing contents.",
                historical_location,
            ))
        text_like = path.suffix.lower() in TEXT_EXTENSIONS or lower_name in {
            "dockerfile", "makefile", "readme", "license", "notice",
        }
        if size > MAX_TEXT_SCAN_BYTES:
            if text_like:
                findings.append(Finding(
                    "blocker", "history-content-scan-incomplete",
                    f"Historical text-like blob exceeds the {MAX_TEXT_SCAN_BYTES // (1024 * 1024)} MiB scan limit.",
                    historical_location,
                ))
            continue
        proc = subprocess.run(
            ["git", "-C", str(root), "cat-file", "blob", sha],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if proc.returncode != 0:
            findings.append(Finding(
                "blocker", "history-content-scan-failed",
                "A reachable historical blob could not be read.", historical_location,
            ))
            continue
        data = proc.stdout
        if not text_like and b"\0" in data[:4096]:
            continue
        scanned += 1
        text = data.decode("utf-8", errors="replace")
        scan_text_lines(text.splitlines(), historical_location, path.suffix, findings, "history-")
    metadata["history_blob_count"] = len(entries)
    metadata["historical_text_blob_count"] = scanned


def scan_content(root: Path, files: Iterable[Path], findings: list[Finding]) -> None:
    for path in files:
        try:
            size = path.stat().st_size
        except OSError as exc:
            findings.append(Finding("blocker", "scan-failed", f"Could not inspect file metadata: {exc}", relative(root, path)))
            continue

        rel = relative(root, path)
        if size >= 100 * 1024 * 1024:
            findings.append(Finding("blocker", "oversize-file", "File is at least 100 MiB.", rel))
        elif size >= 50 * 1024 * 1024:
            findings.append(Finding("warning", "large-file", "File is at least 50 MiB; verify current GitHub limits or LFS intent.", rel))

        relative_path = Path(rel)
        lower_parts = {part.lower() for part in relative_path.parts}
        lower_name = path.name.lower()
        log_file = is_log_path(relative_path)
        if lower_name in SENSITIVE_NAMES or lower_name.startswith(".env.") or path.suffix.lower() in {".key", ".p12", ".pfx", ".pem", ".jks", ".keystore", ".ovpn"}:
            findings.append(Finding("blocker", "sensitive-filename", "Potential credential or private-key file; inspect without disclosing contents.", rel))
        if lower_parts & GENERATED_DIRS:
            findings.append(Finding("warning", "generated-path", "Generated, cache, or editor path appears publishable; verify intent and ignore rules.", rel))
        if path.suffix.lower() in TEMP_SUFFIXES:
            findings.append(Finding("warning", "temporary-file", "Temporary or backup file appears publishable; remove it or document its intent.", rel))
        if log_file:
            findings.append(Finding("warning", "log-artifact", "Log or diagnostic artifact appears publishable; verify that inclusion is necessary.", rel))

        if not is_probably_text(path):
            continue
        if size > MAX_TEXT_SCAN_BYTES:
            findings.append(Finding(
                "blocker", "content-scan-incomplete",
                f"Text-like file exceeds the {MAX_TEXT_SCAN_BYTES // (1024 * 1024)} MiB scan limit.", rel,
            ))
            continue
        try:
            with path.open("r", encoding="utf-8", errors="replace") as handle:
                scan_text_lines(handle, rel, path.suffix, findings)
        except OSError as exc:
            findings.append(Finding("blocker", "scan-failed", f"Could not inspect text content: {exc}", rel))


def inspect_repository(
    root: Path,
    identity_policy: str = "noreply",
    approved_noreply: str | None = None,
    account_error: str | None = None,
) -> tuple[dict[str, object], list[Finding]]:
    findings: list[Finding] = []
    code, _ = git(root, "rev-parse", "--show-toplevel")
    is_git = code == 0
    metadata: dict[str, object] = {"root": str(root), "is_git_repository": is_git}

    if not is_git:
        findings.append(Finding("blocker", "not-git-repository", "No Git repository was detected."))
    else:
        code, branch = git(root, "branch", "--show-current")
        metadata["branch"] = branch if code == 0 and branch else None
        code, head = git(root, "rev-parse", "HEAD")
        metadata["head"] = head if code == 0 else None
        code, status = git(root, "status", "--porcelain=v1", "--untracked-files=all")
        if code != 0:
            findings.append(Finding("blocker", "git-status-failed", "Git status could not be inspected."))
        changed = [line for line in status.splitlines() if line] if code == 0 else []
        metadata["worktree_change_count"] = len(changed)
        if changed:
            findings.append(Finding("warning", "dirty-worktree", f"Worktree contains {len(changed)} changed or untracked path(s)."))
        code, remotes = git(root, "remote", "-v")
        metadata["remotes_configured"] = bool(remotes) if code == 0 else False
        if code != 0:
            findings.append(Finding("blocker", "git-remote-check-failed", "Git remotes could not be inspected."))
        elif not remotes:
            findings.append(Finding("advisory", "no-remote", "No Git remote is configured."))
        scan_git_identities(root, findings, metadata, identity_policy, approved_noreply, account_error)
        try:
            scan_history_content(root, findings, metadata)
        except RuntimeError as exc:
            findings.append(Finding(
                "blocker", "history-content-scan-failed",
                f"Reachable Git history could not be scanned completely: {exc}",
                "git-history",
            ))

    files = candidate_files(root, is_git)
    metadata["candidate_file_count"] = len(files)
    names = {relative(root, path).lower() for path in files}
    if not any(name in names for name in {"readme", "readme.md", "readme.rst", "readme.txt"}):
        findings.append(Finding("blocker", "missing-readme", "No root README was found."))
    if ".gitignore" not in names:
        findings.append(Finding("warning", "missing-gitignore", "No root .gitignore was found; verify that generated and local files are excluded."))
    if not any(name in names for name in {"license", "license.md", "license.txt", "copying"}):
        findings.append(Finding("warning", "missing-license", "No license file was found; do not infer permission to reuse the code."))

    scan_content(root, files, findings)
    rank = {"blocker": 0, "warning": 1, "advisory": 2}
    findings.sort(key=lambda item: (rank[item.severity], item.path or "", item.line or 0, item.code))
    return metadata, findings


def print_text(metadata: dict[str, object], findings: list[Finding]) -> None:
    counts = {level: sum(item.severity == level for item in findings) for level in ("blocker", "warning", "advisory")}
    print(f"Repository: {metadata['root']}")
    print(f"Git: {metadata['is_git_repository']}  Branch: {metadata.get('branch')}  HEAD: {metadata.get('head')}")
    print(f"Candidate files: {metadata['candidate_file_count']}  Worktree changes: {metadata.get('worktree_change_count', 'n/a')}")
    print(f"Findings: {counts['blocker']} blocker(s), {counts['warning']} warning(s), {counts['advisory']} advisory item(s)")
    for item in findings:
        location = ""
        if item.path:
            location = f" {item.path}"
            if item.line:
                location += f":{item.line}"
        print(f"[{item.severity.upper()}] {item.code}{location} - {item.message}")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository", nargs="?", default=".", help="Repository path (default: current directory)")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument(
        "--identity-policy",
        choices=("noreply", "configured"),
        default="noreply",
        help="Require ID-based noreply (default), or allow the exact repository-local email after explicit approval.",
    )
    parser.add_argument("--gh", help="Path to the GitHub CLI executable used to resolve the authenticated account")
    parser.add_argument("--expected-github-id", help="Expected numeric GitHub account ID; use with --expected-github-login")
    parser.add_argument("--expected-github-login", help="Expected GitHub login; use with --expected-github-id")
    parser.add_argument("--strict", action="store_true", help="Return failure when warnings exist")
    args = parser.parse_args()
    root = Path(args.repository).expanduser().resolve()
    if not root.is_dir():
        print(f"error: repository path is not a directory: {root}", file=sys.stderr)
        return 2
    try:
        approved_noreply, account_error = resolve_expected_noreply(
            args.gh, args.expected_github_id, args.expected_github_login,
        )
        metadata, findings = inspect_repository(
            root,
            identity_policy=args.identity_policy,
            approved_noreply=approved_noreply,
            account_error=account_error,
        )
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"error: publication preflight could not complete: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        print(json.dumps({"metadata": metadata, "findings": [asdict(item) for item in findings]}, ensure_ascii=False, indent=2))
    else:
        print_text(metadata, findings)
    if any(item.severity == "blocker" for item in findings):
        return 1
    if args.strict and any(item.severity == "warning" for item in findings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
