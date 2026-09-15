# GitHub Project Publisher v0.1.0

版本：`v0.1.0`

发布类型：稳定版 / Stable

目标分支：`main`

## Release 标题

```text
v0.1.0 — GitHub Project Publisher 初始版本
```

## 中文 Release Notes

这是 GitHub Project Publisher 的首次公开版本。该 Codex Skill 将本地项目上传 GitHub 前的检查、文档撰写、提交组织和发布验证整合为一套可审计流程。

### 主要内容

- 提供审计、本地准备、仓库发布和 Release 发布四种工作模式。
- 提供无第三方依赖的 Python 预检脚本，支持文本和 JSON 输出。
- 检查仓库状态、README、`.gitignore`、许可证状态、文件大小、生成目录和远程配置。
- 对 API Key、访问令牌、密码、私钥、Session/Cookie、含凭证 URL、个人信息和支付凭证实施阻断式检查。
- 检查日志、HAR、trace、dump、崩溃报告，以及可能输出敏感字段的源码日志调用。
- 提供 README 与 Release Notes 的证据驱动写作规范。
- 提供 Conventional Commits、版本一致性和安全 GitHub 发布操作手册。

### 安全行为

发现敏感信息时，预检仅报告风险类别和 `文件:行号`，不会输出匹配值。发现阻断项时返回退出码 `1`；扫描无法完成时返回退出码 `2`。两种情况均要求停止 commit、push、tag 和 Release。

### 兼容性

- Python 3.10 或更高版本；
- Git；
- 支持本地 Skills 的 Codex；
- GitHub CLI 仅用于实际 GitHub 发布操作。

### 已知限制

- 模式匹配不能替代领域专属安全审查。
- 图片、压缩包、加密内容、专有二进制格式和跨变量组合的敏感信息需要额外检查。
- 本 Skill 不提供 GitHub 身份或权限，也不会绕过发布授权。

### 安装

将 `github-project-publisher` 目录复制到 `C:\Users\username\.codex\skills`，然后在 Codex 中使用：

```text
$github-project-publisher 检查当前项目并准备 GitHub 发布。
```

---

## English Release Notes

This is the first public release of GitHub Project Publisher, a Codex skill that turns pre-publication review, documentation, commit preparation, and GitHub verification into an auditable workflow.

### Highlights

- Provides audit-only, local preparation, repository publication, and Release publication modes.
- Includes a dependency-free Python preflight scanner with text and JSON output.
- Reviews repository state, README, `.gitignore`, license status, file sizes, generated paths, and remote configuration.
- Blocks on potential API keys, access tokens, passwords, private keys, sessions/cookies, credential-bearing URLs, personal information, and payment credentials.
- Reviews logs, HAR files, traces, dumps, crash reports, and source logging calls that may expose sensitive fields.
- Includes evidence-based guidance for README and Release Notes.
- Includes Conventional Commits, version-consistency checks, and a safe GitHub publishing runbook.

### Security behavior

When sensitive data is detected, the preflight reports only the category and `path:line`; it never prints the matched value. Exit code `1` indicates blockers, while exit code `2` indicates an incomplete scan. Both stop commit, push, tag, and Release operations.

### Compatibility

- Python 3.10 or later;
- Git;
- a Codex surface with local skill support;
- GitHub CLI only for actual GitHub publication.

### Known limitations

- Pattern matching does not replace domain-specific security review.
- Images, archives, encrypted content, proprietary binary formats, and values assembled across variables require additional inspection.
- The skill does not provide GitHub identity or permission and never bypasses publication authorization.

### Installation

Copy `github-project-publisher` into `C:\Users\username\.codex\skills`, then invoke:

```text
$github-project-publisher Audit this project and prepare it for GitHub publication.
```
