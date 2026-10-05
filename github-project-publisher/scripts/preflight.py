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

# Heuristic portability hints, not proof of private data or broken execution.
LOCAL_PATH_PATTERN = re.compile(
    r"(?<![\w/:\\])(?:[A-Za-z]:[\\/]+[^\s\"'`<>]+"
    r"|/(?:Users|home)/[^\s\"'`<>]+"
    r"|/opt[/][^\s\"'`<>]+"
    r"|/usr/local/(?:bin/(?:python[\w.]*|Rscript|R)|lib/(?:python|R)[^\s\"'`<>]*)"
    r")(?![\w])"
)


def has_machine_local_path(line: str, suffix: str) -> bool:
    for match in LOCAL_PATH_PATTERN.finditer(line):
        path = re.sub(r"\\+", "/", match.group()).casefold().rstrip("/.,;)")
        # Explicit documentation placeholders are not evidence of a local setup.
        if suffix.lower() in {".md", ".rst", ".txt"} and (
            re.match(r"^[a-z]:/path/to(?:/|$)", path)
            or re.match(r"^(?:[a-z]:/users|/users|/home)/(?:username|yourname|example-user)(?:/|$)", path)
        ):
            continue
        return True
    return False


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
    history_identity_policy: str,
    approved_noreply: str | None,
    account_error: str | None,
    publication_refs: list[str],
) -> None:
    code, configured_email = git(root, "config", "--local", "--get", "user.email")
    metadata["identity_policy"] = identity_policy
    metadata["github_account_verified"] = approved_noreply is not None
    if identity_policy != "report" and approved_noreply is None:
        findings.append(Finding(
            "blocker", "github-account-unverified",
            account_error or "Authenticated GitHub account ownership could not be verified.",
            "github-account",
        ))
    metadata["local_noreply_configured"] = code == 0 and is_id_noreply(configured_email)
    if code != 0 or not configured_email:
        severity = "advisory" if identity_policy == "report" else "blocker"
        findings.append(Finding(
            severity, "git-email-not-configured",
            "Repository-local Git email is missing; configure an identity before creating a publication commit.",
            "git-config:user.email",
        ))
    elif identity_policy == "report" and not is_id_noreply(configured_email):
        findings.append(Finding(
            "warning", "git-email-public",
            "The repository-local Git email is a personal address and will be public in new commit metadata; value intentionally redacted.",
            "git-config:user.email",
        ))
    elif identity_policy == "noreply" and not is_id_noreply(configured_email):
        findings.append(Finding(
            "blocker", "git-email-not-noreply",
            "Repository-local Git email is not an ID-based GitHub noreply address; value intentionally redacted.",
            "git-config:user.email",
        ))
    elif identity_policy != "report" and is_id_noreply(configured_email) and approved_noreply and normalized_email(configured_email) != normalized_email(approved_noreply):
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

    if publication_refs:
        code, history = git(root, "log", *publication_refs, "--format=%H%x09%ae%x09%ce")
    else:
        code, history = 0, ""
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
            author_approved = is_approved_email(author_email, configured_email, identity_policy, approved_noreply)
            committer_approved = is_approved_email(committer_email, configured_email, identity_policy, approved_noreply)
            if not author_approved:
                severity = "blocker" if history_identity_policy == "strict" else "advisory"
                findings.append(Finding(
                    severity, "commit-author-email-outside-current-policy",
                    "Existing commit Author identity differs from the current publication identity; this is normal in collaborative history. Value intentionally redacted.",
                    f"commit:{sha}",
                ))
            if not committer_approved:
                severity = "blocker" if history_identity_policy == "strict" else "advisory"
                findings.append(Finding(
                    severity, "commit-committer-email-outside-current-policy",
                    "Existing commit Committer identity differs from the current publication identity; this is normal in collaborative history. Value intentionally redacted.",
                    f"commit:{sha}",
                ))
    metadata["commit_identity_count"] = commit_count

    selected_tags: set[str] = set()
    for ref in publication_refs:
        code, canonical = git(root, "rev-parse", "--symbolic-full-name", ref)
        if code == 0 and canonical.startswith("refs/tags/"):
            selected_tags.add(canonical)
    annotated_count = 0
    for selected_tag in sorted(selected_tags):
        code, tags = git(
            root, "for-each-ref", "--format=%(refname)%09%(objecttype)%09%(taggeremail)", selected_tag,
        )
        if code != 0:
            findings.append(Finding("blocker", "git-tag-identity-scan-failed", "Tag identity metadata could not be inspected.", selected_tag))
            continue
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
                findings.append(Finding("blocker", "git-tag-identity-scan-incomplete", "Unexpected Tag identity metadata format.", selected_tag))
                continue
            refname, object_type, tagger_email = parts
            if object_type != "tag":
                continue
            annotated_count += 1
            if not is_approved_email(tagger_email, configured_email, identity_policy, approved_noreply):
                severity = "blocker" if history_identity_policy == "strict" else "advisory"
                findings.append(Finding(
                    severity, "tagger-email-outside-current-policy",
                    "Existing annotated Tag identity differs from the current publication identity; value intentionally redacted.",
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


def candidate_ref_paths(root: Path, refs: list[str]) -> set[str]:
    paths: set[str] = set()
    for ref in refs:
        code, output = git(root, "ls-tree", "-r", "--name-only", "-z", ref)
        if code != 0:
            raise RuntimeError(f"publication ref paths could not be enumerated: {ref}")
        paths.update(item.replace("\\", "/") for item in output.split("\0") if item)
    return paths


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
        if has_machine_local_path(line, suffix):
            findings.append(Finding(
                "advisory" if code_prefix == "history-" else "warning",
                f"{code_prefix}machine-local-path",
                "Possible machine-specific path; review portability and personal-directory exposure. "
                "Prefer project-relative paths, PATH discovery, or explicit configuration where appropriate. "
                "Value intentionally redacted.",
                rel, number,
            ))
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


def publication_refs(root: Path, requested_refs: Iterable[str] | None) -> list[str]:
    requested = list(requested_refs or [])
    if not requested:
        code, _ = git(root, "rev-parse", "--verify", "HEAD^{commit}")
        return ["HEAD"] if code == 0 else []
    resolved: list[str] = []
    for ref in requested:
        code, _ = git(root, "rev-parse", "--verify", f"{ref}^{{object}}")
        if code != 0:
            raise RuntimeError(f"publication ref could not be resolved: {ref}")
        resolved.append(ref)
    return resolved


def publication_ref_oids(root: Path, refs: Iterable[str]) -> dict[str, str]:
    resolved: dict[str, str] = {}
    for ref in refs:
        code, oid = git(root, "rev-parse", "--verify", f"{ref}^{{object}}")
        if code != 0 or not oid:
            raise RuntimeError(f"publication ref could not be resolved: {ref}")
        resolved[ref] = oid
    return resolved


def worktree_equivalent_blobs(root: Path, files: Iterable[Path]) -> dict[str, str]:
    candidate_paths = {relative(root, path) for path in files}
    code, staged = git(root, "ls-files", "--stage", "-z")
    if code != 0:
        return {}
    tracked: dict[str, str] = {}
    for row in staged.split("\0"):
        if not row or "\t" not in row:
            continue
        fields, path = row.split("\t", 1)
        parts = fields.split()
        normalized = path.replace("\\", "/")
        if len(parts) >= 3 and parts[2] == "0" and normalized in candidate_paths:
            tracked[normalized] = parts[1]

    code, changed = git(root, "diff-files", "--name-only", "-z")
    if code != 0:
        return {}
    unsafe = {path.replace("\\", "/") for path in changed.split("\0") if path}

    code, flags = git(root, "ls-files", "-v", "-z")
    if code != 0:
        return {}
    for row in flags.split("\0"):
        if len(row) >= 3 and row[0].islower() and row[1] == " ":
            unsafe.add(row[2:].replace("\\", "/"))

    return {path: oid for path, oid in tracked.items() if path not in unsafe}


def history_blob_entries(root: Path, refs: list[str]) -> list[tuple[str, str, int]]:
    if not refs:
        return []
    code, output = git(root, "rev-list", "--objects", *refs)
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


def blob_prefix(root: Path, sha: str, limit: int = 4096) -> bytes | None:
    proc = subprocess.Popen(
        ["git", "-C", str(root), "cat-file", "blob", sha],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    try:
        assert proc.stdout is not None
        data = proc.stdout.read(limit)
    finally:
        if proc.stdout is not None:
            proc.stdout.close()
        proc.kill()
        proc.wait()
    return data


def scan_history_content(
    root: Path,
    findings: list[Finding],
    metadata: dict[str, object],
    refs: list[str],
    worktree_blobs: dict[str, str] | None = None,
) -> None:
    entries = history_blob_entries(root, refs)
    scanned = 0
    deduplicated = 0
    equivalent = worktree_blobs or {}
    for sha, path_text, size in entries:
        if path_text and equivalent.get(path_text) == sha:
            deduplicated += 1
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
        if size >= 100 * 1024 * 1024:
            findings.append(Finding(
                "blocker", "history-oversize-file",
                "A file in candidate history is at least 100 MiB; verify current GitHub limits or use Git LFS when appropriate.",
                historical_location,
            ))
        if size > MAX_TEXT_SCAN_BYTES:
            prefix = blob_prefix(root, sha)
            if prefix is None:
                findings.append(Finding(
                    "blocker", "history-content-scan-incomplete",
                    "A historical blob could not be classified for content scanning.",
                    historical_location,
                ))
            elif text_like or b"\0" not in prefix:
                findings.append(Finding(
                    "blocker", "history-content-scan-incomplete",
                    f"Historical text-like blob exceeds the {MAX_TEXT_SCAN_BYTES // (1024 * 1024)} MiB scan limit.",
                    historical_location,
                ))
            else:
                findings.append(Finding(
                    "warning", "history-large-binary-uninspected",
                    "Large historical binary content was not pattern-scanned; verify it with format-appropriate tooling if it will be published.",
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
    metadata["deduplicated_history_blob_count"] = deduplicated


def scan_content(root: Path, files: Iterable[Path], findings: list[Finding]) -> None:
    for path in files:
        try:
            size = path.lstat().st_size
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

        if path.is_symlink():
            try:
                target = os.readlink(path)
                scan_text_lines([target], rel, path.suffix, findings)
            except OSError as exc:
                findings.append(Finding("blocker", "scan-failed", f"Could not inspect symbolic link: {exc}", rel))
            continue
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
    identity_policy: str = "report",
    history_identity_policy: str = "report",
    approved_noreply: str | None = None,
    account_error: str | None = None,
    requested_refs: Iterable[str] | None = None,
    include_worktree: bool = True,
) -> tuple[dict[str, object], list[Finding]]:
    findings: list[Finding] = []
    code, _ = git(root, "rev-parse", "--show-toplevel")
    is_git = code == 0
    metadata: dict[str, object] = {"root": str(root), "is_git_repository": is_git}

    if not is_git:
        findings.append(Finding("blocker", "not-git-repository", "No Git repository was detected."))
    else:
        try:
            refs = publication_refs(root, requested_refs)
        except RuntimeError as exc:
            findings.append(Finding("blocker", "publication-ref-invalid", str(exc), "git-ref"))
            refs = []
        metadata["publication_refs"] = refs
        try:
            metadata["publication_ref_oids"] = publication_ref_oids(root, refs)
        except RuntimeError as exc:
            findings.append(Finding("blocker", "publication-ref-invalid", str(exc), "git-ref"))
            metadata["publication_ref_oids"] = {}
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
        files = candidate_files(root, is_git) if include_worktree else []
        equivalent_blobs = worktree_equivalent_blobs(root, files) if include_worktree else {}
        scan_git_identities(
            root, findings, metadata, identity_policy, history_identity_policy,
            approved_noreply, account_error, refs,
        )
        try:
            scan_history_content(root, findings, metadata, refs, equivalent_blobs)
        except RuntimeError as exc:
            findings.append(Finding(
                "blocker", "history-content-scan-failed",
                f"Reachable Git history could not be scanned completely: {exc}",
                "git-history",
            ))

    if not is_git:
        files = candidate_files(root, is_git) if include_worktree else []
    if is_git and not include_worktree:
        try:
            ref_paths = candidate_ref_paths(root, metadata.get("publication_refs", []))
        except RuntimeError as exc:
            findings.append(Finding("blocker", "publication-ref-paths-failed", str(exc), "git-ref"))
            ref_paths = set()
        names = {name.lower() for name in ref_paths}
        metadata["candidate_file_count"] = len(ref_paths)
    else:
        names = {relative(root, path).lower() for path in files}
        metadata["candidate_file_count"] = len(files)
    metadata["worktree_content_scanned"] = include_worktree
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
        choices=("report", "noreply", "configured"),
        default="report",
        help="Report current identity without blocking (default), require authenticated noreply, or allow the selected repository-local email.",
    )
    parser.add_argument(
        "--history-identity-policy",
        choices=("report", "strict"),
        default="report",
        help="Report collaborative historical identities (default), or require every historical identity to match the selected policy.",
    )
    parser.add_argument(
        "--ref", action="append", dest="refs",
        help="Publication ref to scan; repeat for multiple refs. Defaults to HEAD rather than every local ref.",
    )
    parser.add_argument(
        "--committed-only", action="store_true",
        help="Scan selected committed refs without treating current worktree and untracked content as publication candidates.",
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
    if bool(args.expected_github_id) != bool(args.expected_github_login):
        print("error: --expected-github-id and --expected-github-login are required together", file=sys.stderr)
        return 2
    try:
        if args.identity_policy == "report" and not any((args.expected_github_id, args.expected_github_login)):
            approved_noreply, account_error = None, None
        else:
            approved_noreply, account_error = resolve_expected_noreply(
                args.gh, args.expected_github_id, args.expected_github_login,
            )
        metadata, findings = inspect_repository(
            root,
            identity_policy=args.identity_policy,
            history_identity_policy=args.history_identity_policy,
            approved_noreply=approved_noreply,
            account_error=account_error,
            requested_refs=args.refs,
            include_worktree=not args.committed_only,
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
