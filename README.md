# GitHub Project Publisher

[English](README.en.md) | 简体中文

一个面向 Codex 的 GitHub 项目规范发布 Skill。它以可审计、证据驱动的流程完成上传前检查、敏感信息门禁、README 与 Release 文案撰写、Conventional Commits 组织，以及经明确授权后的 GitHub 发布。

## 项目状态

本仓库包含 GitHub Project Publisher 的 Skill 源码。当前版本为 [`v0.2.0`](https://github.com/cicada478/github-project-publisher/releases/tag/v0.2.0)，版本说明见 [RELEASE_NOTES.md](RELEASE_NOTES.md)。

## 核心能力

- 将任务区分为只读审计、本地准备、仓库发布和 Release 发布四种模式。
- 检查 Git 状态、仓库卫生、文件大小、文档完整性、许可证状态和远程目标。
- 对 API Key、令牌、密码、私钥、Session/Cookie、个人信息和支付凭证实施阻断式审查。
- 检查可发布日志、HAR、trace、dump、崩溃报告，以及源码中的敏感字段日志调用。
- 新建仓库一律先以 Private 上传并完成全套审查，公开转换作为独立的最终人工决策。
- 强制使用当前 GitHub 账户的 ID 型 noreply 地址，并检查所有可达提交的 Author/Committer 和注释 Tag 的 Tagger。
- 对每个用户上传的 Release 资产计算 SHA-256，并与 GitHub 返回的远端 digest 比对。
- 区分需要对话式选择的实质决策与无需提问的强制安全检查。
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
  → 配置并验证 noreply 身份
  → 创建 Private 仓库并上传
  → Release 资产 SHA-256 与远端 digest 比对
  → 全新克隆和远程结果验证
  → 对话式确认是否转为 Public
  → Public 后匿名访问与安全功能复核
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
| Private-first 可见性 | 新仓库必须先 Private 上传、审查和全新克隆验证；转 Public 是独立的最终人工决策 | [GitHub：Setting repository visibility](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility)、[GitHub CLI：`gh repo create`](https://cli.github.com/manual/gh_repo_create)、[安全发布手册](github-project-publisher/references/publishing-runbook.md) |
| Git 提交邮箱隐私 | 使用当前账户的 `ID+USERNAME@users.noreply.github.com`，并阻断非 noreply 的 Author、Committer 和注释 Tag Tagger | [GitHub：Email addresses reference](https://docs.github.com/en/account-and-profile/reference/email-addresses-reference)、[本项目敏感信息审查](github-project-publisher/references/sensitive-data-review.md) |
| 人机决策边界 | 权利、破坏性操作和最终公开状态使用对话式选择；确定性的扫描、SHA、身份与克隆验证自动执行并报告 | [交互与决策策略](github-project-publisher/references/interaction-policy.md) |
| Commit 规范 | 使用 `type(scope)!: subject`、可选 body/footer 和 `BREAKING CHANGE`；提交必须保持单一意图 | [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)、[commitlint config-conventional](https://github.com/conventional-changelog/commitlint/tree/master/@commitlint/config-conventional)、[本项目 Commit 规范](github-project-publisher/references/commit-conventions.md) |
| 版本规则 | 仅在项目声明公共 API 和 SemVer 政策时，将 `fix`、`feat`、破坏性变更分别映射到 PATCH、MINOR、MAJOR | [Semantic Versioning 2.0.0](https://semver.org/) |
| Release 文案与版本发布 | Release 必须绑定明确 Tag 和目标提交；所有用户上传资产必须通过本地 SHA-256 与远端 digest 一致性验证 | [GitHub：About releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)、[GitHub：Release assets API](https://docs.github.com/en/rest/releases/assets)、[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/)、[安全发布手册](github-project-publisher/references/publishing-runbook.md) |
| 许可证标识 | 不替权利人选择许可证；选择后优先使用标准许可证全文与 SPDX 标识 | [SPDX License List](https://spdx.org/licenses/) |

## 目录结构

```text
github-project-publisher/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── commit-conventions.md
│   ├── interaction-policy.md
│   ├── publishing-runbook.md
│   ├── sensitive-data-review.md
│   ├── standards.md
│   └── writing-guide.md
├── scripts/
│   ├── preflight.py
│   └── release_integrity.py
└── tests/
    └── test_preflight.py
```

项目早期提供的 `commit规范.md` 已被吸收并校正到 `references/commit-conventions.md`；发布集合不再依赖仓库根目录的原始文件。

## 环境要求

- 支持本地 Skills 的 Codex；
- Git；
- Python 3.10 或更高版本；
- GitHub CLI（用于身份解析、仓库操作、Release 和远端校验；浏览器仅作为认证或缺失能力的后备方案）。

预检脚本和 Release 完整性验证脚本只使用 Python 标准库；远端 Release 验证还需要 GitHub CLI。

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
$github-project-publisher 将当前项目安全发布到 OWNER/REPOSITORY：先以 private 上传和验证，在最终转为 public 前用对话式选项询问我。
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

预检还会阻断未配置 ID 型 GitHub noreply、本地历史中的非 noreply Author/Committer，以及注释 Tag 中的非 noreply Tagger。它不会回显实际邮箱。

Release 资产上传后执行：

```powershell
python .\github-project-publisher\scripts\release_integrity.py OWNER/REPO TAG .\dist\asset.zip
```

必须列出该 Release 的全部用户上传资产；没有附件时省略文件参数，脚本会报告 `not-applicable`。

## 安全模型

扫描器不会输出匹配到的敏感值。真实凭证如果进入过 Git 历史，应先撤销或轮换，再由仓库所有者评估历史清理；不得通过强制推送临时掩盖问题。安全问题的报告方式见 [SECURITY.md](SECURITY.md)。

## 局限性

- 模式扫描无法证明项目绝对不存在敏感信息。
- 图片、压缩包、加密内容、专有二进制格式和跨变量拼接的秘密需要人工或领域工具检查。
- 本 Skill 不自带 GitHub 账户权限；发布仍依赖本机 Git、GitHub CLI 或已配置的连接能力。
- 严格 noreply 政策会阻断包含非 noreply 历史身份的已有仓库；是否重写已发布历史属于破坏性决策，必须另行授权。
- 仓库专属的测试、构建、许可证和发布策略始终优先于通用建议。

## 许可证

本项目采用 [MIT 许可证](LICENSE)。
