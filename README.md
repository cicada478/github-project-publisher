# GitHub Project Publisher

[English](README.en.md) | 简体中文

一个面向 Codex 的 GitHub 项目规范发布 Skill。它以可审计、证据驱动的流程完成上传前检查、敏感信息门禁、README 与 Release 文案撰写、Conventional Commits 组织，以及经明确授权后的 GitHub 发布。

## 项目状态

本仓库包含 GitHub Project Publisher 的 Skill 源码。当前版本为 [`v0.1.0`](https://github.com/cicada478/github-project-publisher/releases/tag/v0.1.0)，对应说明见 [RELEASE_NOTES.md](RELEASE_NOTES.md)。

## 核心能力

- 将任务区分为只读审计、本地准备、仓库发布和 Release 发布四种模式。
- 检查 Git 状态、仓库卫生、文件大小、文档完整性、许可证状态和远程目标。
- 对 API Key、令牌、密码、私钥、Session/Cookie、个人信息和支付凭证实施阻断式审查。
- 检查可发布日志、HAR、trace、dump、崩溃报告，以及源码中的敏感字段日志调用。
- 根据代码、配置、测试和历史证据撰写 README 与 Release Notes，禁止虚构功能、兼容性和性能结论。
- 使用 Conventional Commits 组织原子提交，并处理 `BREAKING CHANGE`、scope、body 和 footer。
- 在 commit、push、tag 或 Release 前设置明确的人工授权边界。

## 工作流

```text
项目盘点
  → 敏感信息与隐私审查
  → 项目专属 lint/test/build 检查
  → README 与 Release 文案准备
  → 精确审查发布集合
  → 人工确认目标与授权
  → commit / push / tag / Release
  → 远程结果验证
```

发现敏感信息或必要检查失败时，工作流必须停止。报告只包含风险类型和 `文件:行号`，不回显敏感原值。

## 规范依据与来源

本项目没有将单一博客或个人习惯视为通用标准。各项规则优先依据正式规范和平台官方文档，并在 Skill 内转化为可执行检查或操作门禁。

| 规范领域 | 本项目采用方式 | 主要依据 |
| --- | --- | --- |
| Skill 结构与渐进式加载 | `SKILL.md` 声明名称、触发描述和工作流；细则拆分到 `references/`，确定性检查放入 `scripts/` | [OpenAI：Build skills](https://learn.chatgpt.com/docs/build-skills)、[Agent Skills Specification](https://agentskills.io/specification) |
| GitHub 仓库治理 | 要求 README、有效忽略规则、必要验证、明确许可证状态，并区分阻断项、警告项与建议项 | [GitHub：Best practices for repositories](https://docs.github.com/en/repositories/creating-and-managing-repositories/best-practices-for-repositories)、[项目发布标准](github-project-publisher/references/standards.md) |
| README 撰写 | 说明项目用途、价值、安装、最小用例、支持方式、维护状态和限制；所有结论必须有项目证据 | [GitHub：About READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)、[本项目写作指南](github-project-publisher/references/writing-guide.md) |
| 敏感信息与隐私门禁 | 检查凭证、个人信息、支付数据、日志成品和敏感日志调用；命中或检查失败时阻止发布 | [GitHub：Push protection](https://docs.github.com/en/code-security/concepts/secret-security/push-protection)、[本项目敏感信息审查](github-project-publisher/references/sensitive-data-review.md) |
| Commit 规范 | 使用 `type(scope)!: subject`、可选 body/footer 和 `BREAKING CHANGE`；提交必须保持单一意图 | [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)、[commitlint config-conventional](https://github.com/conventional-changelog/commitlint/tree/master/@commitlint/config-conventional)、[本项目 Commit 规范](github-project-publisher/references/commit-conventions.md) |
| 版本规则 | 仅在项目声明公共 API 和 SemVer 政策时，将 `fix`、`feat`、破坏性变更分别映射到 PATCH、MINOR、MAJOR | [Semantic Versioning 2.0.0](https://semver.org/) |
| Release 文案与版本发布 | Release 必须绑定明确 Tag 和目标提交；文案按 Added、Changed、Fixed、Deprecated、Removed、Security 等用户可读类别组织 | [GitHub：About releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)、[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/)、[安全发布手册](github-project-publisher/references/publishing-runbook.md) |
| 许可证标识 | 不替权利人选择许可证；选择后优先使用标准许可证全文与 SPDX 标识 | [SPDX License List](https://spdx.org/licenses/) |

## 目录结构

```text
github-project-publisher/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── commit-conventions.md
│   ├── publishing-runbook.md
│   ├── sensitive-data-review.md
│   ├── standards.md
│   └── writing-guide.md
└── scripts/
    └── preflight.py
```

项目早期提供的 `commit规范.md` 已被吸收并校正到 `references/commit-conventions.md`；发布集合不再依赖仓库根目录的原始文件。

## 环境要求

- 支持本地 Skills 的 Codex；
- Git；
- Python 3.10 或更高版本；
- GitHub CLI（仅在需要创建仓库、推送或发布 Release 时使用）。

预检脚本只使用 Python 标准库，不需要额外安装依赖。

## 安装

### 当前用户级

在 PowerShell 中，从本仓库根目录执行：

```powershell
$skillsRoot = Join-Path $HOME ".codex\skills"
New-Item -ItemType Directory -Force -Path $skillsRoot
Copy-Item -LiteralPath ".\github-project-publisher" -Destination $skillsRoot -Recurse
```

安装结果应为：

```text
C:\Users\username\.codex\skills\github-project-publisher\SKILL.md
```

这里的 `username` 代表 Windows 用户名；当前机器对应的实际根目录为 `C:\Users\Cicada\.codex\skills`。不要多嵌套一层同名目录，`SKILL.md` 必须直接位于 `github-project-publisher` 文件夹下。

Codex 通常会自动发现 Skill；如果没有出现，请打开新任务或重启 Codex。在 CLI 或 IDE 扩展中可使用 `/skills` 检查。需要团队分发时，应发布整个 `github-project-publisher` 目录，由每位用户复制到自己的 `.codex\skills` 目录。

## 使用

显式调用最确定：

```text
$github-project-publisher 检查当前项目，只输出上传前审计报告，不修改文件。
```

```text
$github-project-publisher 检查当前项目，修复可安全处理的问题，撰写 README 和 Release 文案，但不要提交或上传。
```

```text
$github-project-publisher 将当前项目发布到 OWNER/REPOSITORY，仓库设为 private，发布 main 分支；创建 Release 前再次向我确认版本号和目标提交。
```

`agents/openai.yaml` 允许隐式调用，因此“检查项目并准备上传 GitHub”等请求也可能自动启用本 Skill。

## 独立运行预检

从本仓库根目录执行：

```powershell
python .\github-project-publisher\scripts\preflight.py .
```

JSON 输出：

```powershell
python .\github-project-publisher\scripts\preflight.py . --format json
```

退出码：

- `0`：内置扫描完成且没有阻断项；仍需执行项目专属检查。
- `1`：发现阻断项，不得提交或发布。
- `2`：扫描未能完成，按阻断项处理。

## 安全模型

扫描器不会输出匹配到的敏感值。真实凭证如果进入过 Git 历史，应先撤销或轮换，再由仓库所有者评估历史清理；不得通过强制推送临时掩盖问题。安全问题的报告方式见 [SECURITY.md](SECURITY.md)。

## 局限性

- 模式扫描无法证明项目绝对不存在敏感信息。
- 图片、压缩包、加密内容、专有二进制格式和跨变量拼接的秘密需要人工或领域工具检查。
- 本 Skill 不自带 GitHub 账户权限；发布仍依赖本机 Git、GitHub CLI 或已配置的连接能力。
- 仓库专属的测试、构建、许可证和发布策略始终优先于通用建议。

## 许可证

本项目采用 [MIT 许可证](LICENSE)。
