# README and release writing guide

## README: design from reader tasks

Start with the shortest path from discovery to a verified result. Select sections because the project needs them, not to satisfy a template.

### Opening block

State the project name and one precise sentence answering: what is it, for whom, and what result does it produce? Follow with maturity/status and the most important constraint. Use badges sparingly; every badge must convey maintained, decision-relevant state.

### Recommended information architecture

1. **Overview** — problem, scope, non-goals, and distinguishing approach.
2. **Quick start** — prerequisites, installation, minimal command/example, and expected observable result.
3. **Usage** — representative workflows ordered by user importance; link exhaustive API material elsewhere.
4. **Configuration** — names, types, defaults, precedence, secret-handling, and safe examples.
5. **Development and validation** — supported toolchain, setup, lint/test/build commands, and contribution route.
6. **Reproducibility or architecture** — include only if users or reviewers need it; identify inputs, versions, seeds, hardware, datasets, and known sources of variance.
7. **Limitations and status** — known failure modes, unsupported environments, stability, and compatibility policy.
8. **Support, security, license, citation, and acknowledgements** — link dedicated files where they exist.

For a library, define the public API and compatibility promise. For a CLI, document command syntax and exit behavior. For a service, document deployment assumptions and health verification. For research software, document method, data provenance, environment capture, reproduction procedure, evaluation definition, and citation.

### Style rules

- Prefer falsifiable, specific claims over promotional adjectives.
- Keep terminology consistent with code and UI.
- Use relative repository links and fenced blocks with the correct language identifier.
- Never put live credentials in examples; use unmistakable placeholders such as `YOUR_API_TOKEN`.
- Avoid screenshots for information that changes frequently or must be accessible/searchable.
- Do not claim cross-platform support unless tested or otherwise evidenced.
- Treat benchmark numbers as incomplete without workload, environment, method, sample count, baseline, and date/revision.

### Bilingual README organization

When maintaining Chinese and English READMEs, keep one complete document per language and reciprocal language links near the title. Preserve the repository's existing default language and filenames; this project uses Chinese `README.md` and English `README.en.md`. Do not rename files merely to match a reference project.

Update both versions for changes to capabilities, installation, commands, defaults, limitations, and project status. Keep technical facts equivalent and preserve literal commands, flags, versions, and identifiers; write natural prose for each audience rather than alternating translations sentence by sentence. Link to the matching language of supporting documentation when available. Audience-specific support links may differ when verified, but do not silently omit a functional limitation or change the supported workflow in one language.

The [English](https://github.com/deepseek-ai/deepseek-harness/blob/master/README.md) and [Chinese](https://github.com/deepseek-ai/deepseek-harness/blob/master/README.zh.md) DeepSeek Harness READMEs illustrate separate complete documents, reciprocal navigation, equivalent run commands, and localized supporting links. Reuse these organization choices, not its product claims, installation commands, support channels, or file naming as universal requirements.

## Release notes: communicate change and consequence

Derive notes from the candidate range, not memory. Determine the previous release/tag and inspect the diff, merged PRs, issues, commit history, package metadata, and verification results.

### Language and presentation

Write release notes in both Simplified Chinese and English unless the user explicitly requests otherwise. Put the complete Chinese section first, followed by the complete English section. Keep facts, scope, severity, migration steps, and verification results equivalent; use natural phrasing rather than literal sentence-by-sentence translation. Preserve command names, flags, versions, paths, and identifiers. Shared metadata and comparison links may appear once with bilingual labels.

For a bilingual Release on one page, add `[中文](#release-zh) | [English](#release-en)` before the language sections and provide matching explicit anchors. Keep each language readable on its own instead of alternating translated bullets. Use unique anchors when several releases share one local document, and verify navigation on the target renderer. Contributor credit and shared comparison metadata need not be duplicated. The [DeepSeek Harness dsh-v0.2.1-rc.3 Release](https://github.com/deepseek-ai/deepseek-harness/releases/tag/dsh-v0.2.1-rc.3) illustrates same-page language navigation, separate language blocks, inline credits, and a shared comparison link. Retain this Skill's default emoji categories and Chinese-first ordering unless overridden; the reference's category names are not a replacement policy.

Use the adaptable template below. Omit empty or irrelevant sections, and keep small releases to a summary and a few concrete changes per language. Put actionable security updates or breaking changes before ordinary changes in both languages when applicable. Do not assert compatibility, absence of known issues, or successful checks merely to fill a section.

### Release header

- **Title:** version/tag plus a short factual theme; avoid repeating marketing slogans.
- **Summary:** audience, principal outcome, and stability classification.
- **Date:** use an unambiguous ISO date when included.

### Body

Use only relevant sections:

- **Highlights** — a small set of user-important outcomes.
- **Added / Changed / Fixed / Deprecated / Removed / Security** — Keep a Changelog categories where they improve scanning.
- **Breaking changes and migration** — old behavior, new behavior, affected users, exact migration steps, and rollback considerations.
- **Compatibility** — runtime/platform/API/data-format requirements.
- **Known issues** — impact, conditions, workaround, and tracking link if available.
- **Verification** — checks actually run against the release candidate and their result.
- **Install or upgrade** — exact commands and asset choice, if not obvious.
- **Contributors and full diff** — credit from verified history; link the comparison range.

Do not dump raw commit messages, describe internal refactors as user features, or say “various fixes.” Link issue/PR identifiers only when they resolve correctly in the destination repository. For a security fix, avoid exploit-enabling detail before coordinated disclosure; use the repository's security advisory process.

### What's Changed: grouping and visual cues

Use a `本次更新` / `What's Changed` section and the following fixed default category pairs. Keep the same emoji, meaning, and order in both languages. Follow an explicit user preference or an established repository convention when it differs; otherwise use these pairs consistently rather than inventing a new icon or title for each release.

| Chinese heading | English heading | Use for |
| --- | --- | --- |
| ⚠️ 破坏性变更 | ⚠️ Breaking changes | Incompatible changes and required migration |
| 🔒 安全 | 🔒 Security | Security fixes and actionable security guidance |
| ✨ 新增 | ✨ Features | New capabilities |
| 🐛 修复 | 🐛 Fixes | Corrected behavior |
| 🔄 变更 | 🔄 Changes | Other user-visible behavior changes |
| 🕰️ 弃用 | 🕰️ Deprecated | Features still available but scheduled for retirement |
| 🗑️ 移除 | 🗑️ Removed | Removed capabilities |
| 📚 文档与维护 | 📚 Docs & Chores | Relevant documentation and maintenance |
| 📦 依赖更新 | 📦 Dependencies | Dependency changes with relevant effects |

Include only categories supported by actual changes. Put actionable security or breaking-change guidance before ordinary changes, ordered by urgency when necessary. Do not duplicate the same change under multiple categories just to fill headings.

Use emojis as scanning aids alongside explicit text, never as the sole indication of meaning or severity. Avoid decorating every bullet, command, or link. For very small releases, use a flat list with category labels instead of many one-item headings. Group related changes and lead each bullet with a concrete outcome or corrected behavior; add verified PR links and contributor credits when useful. Include maintenance or dependency details when they help the intended reader understand the release, without mechanically listing every internal update.

### Full changelog and contributor credit

When the previous version and current release refs are known and verified, include one shared comparison link at the end using this format:

```markdown
**完整变更 / Full Changelog**: [`vPREVIOUS...vCURRENT`](https://github.com/OWNER/REPO/compare/vPREVIOUS...vCURRENT)
```

Use the actual destination and release range, not assumed tag names. Verify the refs and link before publication; a draft may retain a clearly marked pending link until its candidate tag exists. For a first release with no previous version, omit the comparison range and optionally link the released source. If the range cannot be established, report the missing information instead of inventing a URL.

Check contributor attribution against merged PRs, commits, or GitHub-generated release notes for the candidate range. Preserve accurate existing credits and include verified release contributors when useful, either beside their changes or in an optional `贡献者` / `Contributors` section. A separate section is not required when inline credits already suffice or a solo release needs no additional list. Do not copy contributors from a reference project, infer a GitHub handle from a personal email, expose private identity information, or invent acknowledgements to fill the template.

Use `首次贡献者` / `New Contributors` only when a first contribution to the repository is verified; absence from the current range is not evidence of first-time status. Prefer profile and PR links for text credits. GitHub's avatar display, as shown on a Release page, is presentation rather than a required Markdown artifact: do not require downloaded avatars, HTML layouts, or a matching avatar strip, and do not promise that a text section will reproduce that UI. GitHub-generated notes can supply contributors and comparison links, but review their accuracy and scope before use; see [GitHub's generated release notes documentation](https://docs.github.com/en/repositories/releasing-projects-on-github/automatically-generated-release-notes).

### Adaptable bilingual template

Replace all placeholders with verified candidate facts and remove inapplicable sections before publication. The title theme is bilingual; project names and the version need not be repeated. Repeat categories only when needed, and add verified PR links or contributor credits to individual changes when useful. For a first release without a previous tag, omit the comparison link or link the released source instead of inventing a range.

```markdown
# vX.Y.Z — 中文主题 / English theme

发布日期 / Release date: YYYY-MM-DD
发布类型 / Release type: 稳定版 / Stable [或预发布 / or Prerelease; select one]

[中文](#release-zh) | [English](#release-en)

<a id="release-zh"></a>

## 中文

[一两句说明面向哪些用户、主要变化及影响。]

### 本次更新

#### ✨ 新增

- [能力及其用户价值。]

#### 🐛 修复

- [触发条件、原有问题和修复后的行为。]

#### 🔄 变更

- [用户可观察到的变化。]

#### 📚 文档与维护

- [对使用或开发有帮助的文档与维护改进。]

#### 📦 依赖更新

- [相关依赖变更及其兼容性、安全性或使用影响。]

### 兼容性与升级
[有证据的兼容性要求；如有破坏性变更，说明受影响用户、迁移步骤与回滚注意事项，并将此节前置。]
[适用的安装或升级命令、资产选择。]

### 已知问题
[影响、触发条件、规避方式及有效的跟踪链接。]

### 验证
[对候选版本实际执行的检查及结果；与本次发布相关的未验证事项。]

<a id="release-en"></a>

## English

[One or two sentences matching the Chinese audience, main changes, and impact.]

### What's Changed

#### ✨ Features

- [Capability and user benefit.]

#### 🐛 Fixes

- [Trigger, previous problem, and corrected behavior.]

#### 🔄 Changes

- [User-observable change.]

#### 📚 Docs & Chores

- [Documentation or maintenance improvements relevant to users or developers.]

#### 📦 Dependencies

- [Relevant dependency changes and their compatibility, security, or usage impact.]

### Compatibility and upgrade
[Evidence-backed requirements; for breaking changes, identify affected users, migration steps, and rollback considerations, and move this section before ordinary changes.]
[Applicable install or upgrade commands and asset choice.]

### Known issues
[Impact, conditions, workaround, and valid tracking link.]

### Verification
[Checks actually run against the candidate and their results; relevant unverified areas.]

### 贡献者 / Contributors
[可选：经核实的本版本贡献者及个人主页链接；已有行内署名足够时省略。]
[Optional: verified release contributors and profile links; omit when inline credit suffices.]

**完整变更 / Full Changelog**: [`vPREVIOUS...vX.Y.Z`](https://github.com/OWNER/REPO/compare/vPREVIOUS...vX.Y.Z)
```

### Reference example

[GitHub CLI v2.102.0](https://github.com/cli/cli/releases/tag/v2.102.0) demonstrates prioritizing security guidance, grouping changes, and linking PRs, contributors, and the full comparison range. Borrow those structural choices when useful. Its English-only format does not satisfy this skill's bilingual requirement; its detailed maintenance and dependency lists are optional, not a requirement to reproduce every PR. Summarize changes according to their effect on this project's users.

### Annotated cases: choose structure from the release facts

Read these contrasts when choosing categories, comparison links, or contributor presentation. They illustrate decisions; use the current project's facts and users rather than copying names, changes, or release numbers.

**Observed patch release — [GitHub CLI v2.103.2](https://github.com/cli/cli/releases/tag/v2.103.2):** The release places two attachment-related corrections under `🐛 Fixes`, credits the PR authors inline, identifies a first-time contributor in `New Contributors`, and links the `v2.103.1...v2.103.2` comparison. Its page also displays contributor avatars.

- **Decision to reuse:** A fixes-only release can use a single relevant change category; do not add empty Features or Dependencies headings. Keep the compare range visible and contributor credit traceable to the actual PRs.
- **Boundary:** The first-time designation belongs to that repository's verified history. The avatar display is not a required authoring step. For this Skill, write equivalent Chinese and English coverage unless overridden; do not copy the example's English-only format or its contributor list.

**Hypothetical first release — a solo CLI project with verified initial source and no previous tag:** Use only categories supported by its initial capabilities and relevant documentation. Link the released source if useful, omit the nonexistent version comparison, and omit a separate contributor list when it adds no information.

- **Reason:** The same presentation defaults apply, but the absence of a previous version changes which link can truthfully be provided. The absence of a separate contributor section does not imply missing attribution.
- **Failure to avoid:** Inventing a `v0.0.0...v1.0.0` range or importing names and PR links from the reference release to make the template look complete.

## Editorial acceptance test

Before saving either artifact, verify:

- a new reader can identify whether the project fits their need;
- bilingual READMEs have reciprocal language links and equivalent technical facts; bilingual Releases have working language navigation and complete, equivalent language blocks;
- the first-use procedure is complete and executable;
- every capability and compatibility claim has evidence;
- limitations are as visible as strengths;
- links, anchors, filenames, commands, and versions agree with the candidate revision;
- release notes include equivalent Chinese and English coverage unless the user explicitly requested another language arrangement;
- category pairs follow the defaults or an explicit user/repository convention, with irrelevant headings removed;
- the shared Full Changelog link uses verified release refs when a prior version exists; first-release or unresolved-range exceptions are handled explicitly;
- contributor and first-time contributor claims are verified, with no private identity disclosure or copied reference-project credits;
- prose is concise, neutral, grammatical, and free of unexpanded acronyms where the audience may not know them.
