# GitHub Project Publisher v0.2.0

发布类型：`稳定版 / Stable`

发布日期：`2026-09-28`

版本：`v0.2.0`

目标分支：`main`

目标提交：由附注标签 `v0.2.0` 固定。

## Release 标题

```text
v0.2.0 — Privacy-first publishing gates
```

## 中文 Release Notes

v0.2.0 将 GitHub 发布流程升级为“隐私优先、私有仓库先行、公开前独立放行”的强制门禁，并补齐 Git 身份元数据与 Release 资产完整性检查。

### 新增

- 新仓库必须先创建为 Private，在私有状态完成上传、敏感信息审查和全新克隆验证，避免未经审查的凭证、个人信息或其他敏感内容直接暴露；全部通过后，才单独询问是否转为 Public。
- 新增对话决策规范：仅对可选、歧义或破坏性事项使用结构化选项；强制检查自动执行并报告结果。
- 强制使用 GitHub ID 型 `noreply` 邮箱，并检查仓库配置、全部可达提交的 Author/Committer，以及附注标签的 Tagger 身份。
- 新增 `release_integrity.py`，计算本地 Release 资产 SHA-256，并与 GitHub Release API 返回的远端摘要逐项比对。
- 新增标准库单元测试，覆盖身份门禁和 Release 资产完整性检查。

### 变更

- GitHub CLI 与 Git 成为发布操作的首选工具；浏览器自动化仅用于交互式认证或 CLI 确实不支持的操作。
- Public 转换前必须从远端执行全新克隆，并在克隆副本中复核历史、标签、文档和必要测试。
- 预检发现真实邮箱或非 GitHub ID 型 `noreply` 身份时，将作为阻断项停止提交、推送、标签、Release 或公开操作。
- Release 无用户资产时明确报告 SHA-256 检查为“不适用”，而不是静默跳过。

### 行为兼容性说明

- 现有仓库只要任一可达提交或附注标签含非合规邮箱，就会被新门禁阻断；修复历史前不得公开。
- 从 Private 转为 Public 始终需要最后一次明确决定，不会与仓库创建或首次推送合并执行。

### 验证

- Skill 结构与元数据检查通过。
- 7 项标准库单元测试通过。
- 当前仓库预检通过。
- Markdown 相对链接与 `git diff --check` 检查通过。
- 发布前验证最终提交的 Author、Committer 与附注标签 Tagger 均为 GitHub ID 型 `noreply`。
- 本版本不上传用户提供的 Release 资产；SHA-256 资产门禁记录为不适用。

### 已知限制

- 模式匹配不能替代领域专属安全审查。
- 图片、压缩包、加密内容、专有二进制格式和跨变量组合的敏感信息仍需要额外检查。
- Git 历史重写、远端替换、标签或 Release 替换属于高影响操作，必须单独确认。

### 安装

将 `github-project-publisher` 目录复制到 `C:\Users\username\.codex\skills`，然后在 Codex 中调用：

```text
$github-project-publisher 检查当前项目，修复可安全处理的问题并准备 GitHub 发布。
```

---

## English Release Notes

v0.2.0 makes GitHub publication privacy-first: new repositories begin private, publication is verified before exposure, and changing visibility to public is a separate gated decision. It also adds Git identity-metadata controls and Release asset integrity verification.

### Added

- New repositories must be created Private so upload, sensitive-data review, and fresh-clone verification can finish before exposure, preventing unreviewed credentials, personal information, or other sensitive content from becoming public. Only after all checks pass is public conversion offered as a separate decision.
- A conversational decision policy: structured choices are reserved for optional, ambiguous, or destructive decisions; mandatory checks run automatically and report their results.
- GitHub ID-based `noreply` email enforcement for repository configuration, Author and Committer fields in every reachable commit, and Tagger fields in annotated tags.
- `release_integrity.py` computes each local Release asset's SHA-256 digest and compares it with the digest returned by the GitHub Releases API.
- Standard-library unit tests covering identity gates and Release asset integrity behavior.

### Changed

- GitHub CLI and Git are the preferred publication tools. Browser automation is a fallback only for interactive authentication or capabilities the CLI does not provide.
- A fresh clone from the private remote is required before public visibility, followed by history, tag, documentation, and applicable test verification.
- A real email address or any identity that is not a GitHub ID-based `noreply` address is now a blocking preflight finding.
- Releases with no user-provided assets explicitly report SHA-256 verification as “not applicable” instead of silently skipping it.

### Behavioral compatibility

- Existing repositories are blocked if any reachable commit or annotated tag contains a noncompliant email identity. The history must be remediated before publication.
- Private-to-Public conversion always requires a final explicit decision; it is never bundled with repository creation or the initial push.

### Verification

- Skill structure and metadata checks pass.
- All seven standard-library unit tests pass.
- The repository preflight passes.
- Markdown relative-link validation and `git diff --check` pass.
- The final Author, Committer, and annotated-tag Tagger identities are verified as GitHub ID-based `noreply` addresses before publication.
- This release has no user-supplied Release assets; the SHA-256 asset gate is recorded as not applicable.

### Known limitations

- Pattern matching does not replace domain-specific security review.
- Images, archives, encrypted content, proprietary binary formats, and values assembled across variables still require additional inspection.
- History rewrites, remote replacement, and tag or Release replacement are high-impact operations that require separate confirmation.

### Installation

Copy `github-project-publisher` to `C:\Users\username\.codex\skills`, then invoke:

```text
$github-project-publisher Audit this project, safely fix eligible issues, and prepare it for GitHub publication.
```
