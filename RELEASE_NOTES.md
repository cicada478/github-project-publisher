# GitHub Project Publisher v0.4.1

发布日期 / Release date: `2026-10-04`

发布类型 / Release type: `稳定版 / Stable`

目标分支 / Target branch: `main`; 目标提交由附注标签 / Target commit pinned by annotated tag: `v0.4.1`.

## 中文 Release Notes

v0.4.1 小幅改进 GitHub CLI 操作指导，保持个人项目上传流程轻量、独立可用。

- 仓库与 Release 状态查询使用明确的 JSON 字段；Release 创建和查询显式指定目标仓库，减少对当前工作目录的依赖。
- 需要澄清命令、输出或分页时，可参考官方 `gh` Skill 或本机命令帮助；不新增必装依赖，不自动安装或更新其他 Skill。
- 查询完整列表时提醒处理结果上限与 API 分页。现有发布范围、授权和验证要求保持不变。

兼容性：无脚本、配置或数据格式变更。覆盖安装 Skill 文件夹即可升级。

## English Release Notes

v0.4.1 refines GitHub CLI guidance while keeping personal project publication lightweight and self-contained.

- Query repository and Release state with explicit JSON fields, and target the repository explicitly when creating or viewing a Release.
- Consult the optional official `gh` skill or local command help when syntax, output, or pagination needs clarification. No new required dependency or automatic skill installation is introduced.
- Account for result limits and API pagination when complete lists are needed. Publication scope, authorization, and verification requirements remain unchanged.

Compatibility: no script, configuration, or data-format changes. Upgrade by replacing the installed skill folder.

## 验证 / Verification

- 23 项单元测试通过 / All 23 unit tests passed.
- 12 个行为 eval 场景的结构与覆盖校验通过；未运行真实模型 eval / The 12-case behavior corpus passed structure and coverage validation; live model evals were not run.
- 本版本不附加上传资产 / No uploaded release assets are included.

[完整变更 / Full changelog](https://github.com/cicada478/github-project-publisher/compare/v0.4.0...v0.4.1)

---

# GitHub Project Publisher v0.4.0

发布类型：`稳定版 / Stable`

发布日期：`2026-10-04`

版本：`v0.4.0`

目标分支：`main`

目标提交：由附注标签 `v0.4.0` 固定。

## Release 标题

```text
v0.4.0 — Adaptive GitHub publication workflow
```

## 中文 Release Notes

v0.4.0 将 Skill 从偏向单作者、高强度门禁的发布流程扩展为适用于普通项目和协作仓库的风险自适应 GitHub 发布助手。隐私检查仍然是硬门禁，但扫描范围、身份判断、证据复用和外部操作会根据实际候选内容与发布目标执行，减少无关检查和误阻断。

### 新增

- 最终推送门禁支持 `--committed-only --ref REF`，可精确限定将要发布的分支或标签；多个候选引用可重复传入 `--ref`。
- 新增显式的 `--history-identity-policy strict`，在确实需要单身份历史审查时保留严格模式。
- 新增候选引用 OID、历史去重数量和工作树扫描状态等机器可读元数据。
- 新增协作历史、精确引用、仅提交内容、大型无扩展名文本、扫描去重及旧秘密保留等测试覆盖。

### 变更

- 既有 Author、Committer、Tagger、Bot 和导入历史默认作为来源信息报告，不再因为不同于当前发布者而阻断普通协作仓库。
- 只读审计默认使用报告模式，无需 GitHub 登录；工作流创建的新提交和附注标签仍执行经过账户核验的身份策略。
- 大型无扩展名历史文本不再静默跳过；符号链接按链接本身检查，不跟随到仓库外部。
- 新建且最终准备公开的仓库继续使用 Private-first 和最终公开确认；既有仓库保留原有可见性与协作流程。
- 默认 Skill 提示改为只读审计，不再隐含授权创建仓库或上传内容。
- 工作树中与候选历史完全相同的已跟踪 Blob 只扫描一次；已修改文件仍同时检查工作树内容与旧候选历史。
- 检查证据绑定候选 ref OID、身份策略、相关配置、资产、目标和远端状态；输入未改变时可以安全复用。
- 身份、交互、敏感数据和发布规则收敛到各自的权威参考文件，减少上下文冗余和规则漂移。

### 兼容性说明

- 没有破坏性配置、命令行或数据格式变更；原有默认调用方式继续有效。
- 普通协作历史不再因作者身份不同而失败。需要原有单身份约束的工作流应显式启用严格历史身份策略。
- 二进制、图片、压缩包、加密内容、专有格式和跨变量拼接的秘密仍需人工或领域工具复核。

### 验证

- 23 项 Python 标准库单元测试通过。
- 12 个行为 eval 场景的结构与覆盖校验通过。
- Skill 元数据、UI 配置、本地 Markdown 链接和 `git diff --check` 通过。
- 最终提交引用执行敏感信息与 GitHub noreply 身份门禁，结果为 0 个 blocker。
- 本版本不上传用户提供的 Release 资产；SHA-256 资产门禁记录为不适用。

### 安装或升级

将 `github-project-publisher` 目录复制到项目级或用户级 `.codex\skills` 目录，覆盖旧版本后重新打开任务或重启 Codex。

---

## English Release Notes

v0.4.0 expands the Skill from a strict, single-author-oriented gate into a risk-adaptive GitHub publication assistant for routine projects and collaborative repositories. Privacy checks remain hard gates, while scan scope, identity handling, evidence reuse, and external operations now follow the actual publication candidate and destination.

### Added

- A final `--committed-only --ref REF` gate that scopes publication checks to the exact branches or tags being pushed, with repeatable `--ref` arguments for multiple candidates.
- An explicit `--history-identity-policy strict` mode for workflows that genuinely require single-identity history review.
- Machine-readable candidate ref OIDs, history deduplication counts, and worktree-scan state.
- Test coverage for collaborative history, exact ref scoping, committed-only publication, large extensionless text, scan deduplication, and retained historical secrets.

### Changed

- Existing Authors, Committers, Taggers, bots, and imported history are provenance by default instead of failures merely because they differ from the current publisher.
- Read-only audits default to report-only identity handling without GitHub authentication; workflow-created commits and annotated tags still use account-verified identity gates.
- Large extensionless historical text is no longer silently skipped, and symbolic links are inspected without following targets outside the repository.
- Private-first remains required for newly created destinations whose final state is public, while existing repositories retain their visibility and collaboration workflow.
- The default Skill prompt is audit-only and no longer implies authorization to create a repository or upload content.
- Tracked worktree content identical to a candidate-history Blob is scanned once; modified files still cause both worktree content and prior candidate history to be checked.
- Evidence is tied to candidate ref OIDs, identity policy, relevant configuration, assets, destination, and remote state, allowing safe reuse while inputs remain unchanged.
- Identity, interaction, sensitive-data, and publication rules now live in focused authoritative references, reducing context duplication and policy drift.

### Compatibility

- There are no breaking configuration, command-line, or data-format changes; existing default invocations remain valid.
- Collaborative history no longer fails solely because contributors use different identities. Workflows that require the previous single-identity constraint should explicitly enable strict history identity review.
- Binaries, images, archives, encrypted content, proprietary formats, and secrets assembled across variables still require manual or domain-specific review.

### Verification

- All 23 Python standard-library unit tests pass.
- The 12-case behavior eval corpus passes structure and coverage validation.
- Skill metadata, UI configuration, local Markdown links, and `git diff --check` pass.
- The final committed ref passes sensitive-data and GitHub noreply identity gates with zero blockers.
- This release has no user-supplied Release assets; the SHA-256 asset gate is recorded as not applicable.

### Install or upgrade

Copy the `github-project-publisher` directory into a project- or user-scoped `.codex\skills` directory, replacing the previous version, then reopen the task or restart Codex.

---

# GitHub Project Publisher v0.3.1

发布类型：`稳定版 / Stable`

发布日期：`2026-10-02`

版本：`v0.3.1`

目标分支：`main`

目标提交：由附注标签 `v0.3.1` 固定。

## Release 标题

```text
v0.3.1 — Verifiable privacy and interaction gates
```

## 中文 Release Notes

v0.3.1 将原有“规范驱动”的发布流程补强为可自动验证的安全门禁：敏感信息检查现在覆盖可达 Git 历史，noreply 身份必须属于当前 GitHub 账户，结构化选项卡同时受语义条件和宿主运行能力约束，并新增行为 eval 与持续集成。本补丁版同时修复 GitHub Actions 标签事件中轻量标签引用被误判为 Tagger 元数据损坏的问题。

### 新增

- 自动枚举并扫描全部可达 Git 历史文本 Blob。即使敏感值已经从当前工作树删除，只要仍存在于可达历史中，就会阻止提交和发布。
- 通过 `gh api user` 核验 GitHub ID 型 noreply 地址的账户归属；仅满足地址格式但属于其他账户的身份不再通过。
- 为无网络 CI 增加可信账户参数 `--expected-github-id` 与 `--expected-github-login`，并支持通过 `--gh` 指定 GitHub CLI 路径。
- 新增 10 个 Skill 行为 eval 场景，覆盖直接与隐式触发、负向触发、不完整输入、结构化选项、二元确认、自由文本、宿主权限、自动检查和阻断行为。
- 新增结构化 eval 结果 Schema 和可选的 `codex exec` 只读行为测试执行器。
- 新增 GitHub Actions：普通 push/PR 执行确定性测试和语料校验；手动工作流可在显式启用并配置凭证后运行真实 Codex 行为 eval。
- 新增 Skill 元数据、UI 配置和 Markdown 相对链接测试。

### 变更

- 选项卡规则改为双重门禁：只有存在尚未解决的实质决策时才满足语义门禁；只有当前回合真实提供 `request_user_input` 或等价工具时才满足运行时门禁。
- 当 `request_user_input` 可用且决策条件满足时，Skill 必须调用该工具，不得用 Markdown 模拟卡片；工具不可用时必须停在变更边界，且不得声称 Skill 能自行开启 Plan 模式。
- Git 身份策略允许用户在结构化决策后选择个人邮箱，但会警告其永久暴露在公开 Git 元数据中；未获批准的其他身份仍然阻断。
- 预检增加历史 Blob 数量、已扫描历史文本数量和 GitHub 账户验证状态等机器可读元数据。
- `.tmp`、本地行为 eval 输出及其他测试残留被排除在发布集合之外。
- README 中英文版补充运行模式、选项卡条件、历史扫描、账户核验、行为 eval 和 CI 使用说明。

### 安全性

- 删除当前文件不再被视为清除历史泄露；可达历史中的高置信敏感模式会以完全脱敏的位置报告阻断发布。
- 任一历史对象无法枚举、读取或完成必要扫描时，流程按检查失败处理并阻断发布。
- noreply 验证从“格式正确”提升为“格式正确且与已认证账户 ID/登录名一致”。

### 兼容性说明

- 默认 noreply 策略现在会阻断属于其他 GitHub 账户的 noreply Author、Committer 或附注 Tag Tagger；这是更严格的身份归属检查。
- 个人邮箱模式仍只允许明确选择的仓库级邮箱，以及属于已核验账户的 noreply 地址。
- 历史扫描会增加大型仓库的预检时间；二进制、图片、压缩包、加密内容和专有格式仍需领域工具或人工复核。
- 选项卡是否可显示仍取决于 Codex 宿主、当前模式、版本和账户能力；Skill 只能在工具可用时调用，不能自行注入界面控件。
- GitHub Actions 标签事件可能把当前标签检出为无 Tagger 的轻量引用；预检现在正确跳过其 Tagger 检查，同时继续严格检查真正的附注标签。

### 验证

- 16 项 Python 标准库单元测试通过。
- 10 个行为 eval 场景的结构与覆盖校验通过。
- Skill 元数据、UI 配置与本地 Markdown 相对链接检查通过。
- `git diff --check` 通过。
- 干净临时仓库严格预检通过：0 个 blocker、0 个 warning。
- 当前仓库的可达提交 Author/Committer、附注 Tag Tagger 与 GitHub 认证账户归属检查通过。
- 本版本不上传用户提供的 Release 资产；SHA-256 资产门禁记录为不适用。

### 安装或升级

将 `github-project-publisher` 目录复制到项目级或用户级 `.codex\skills` 目录，覆盖旧版本后重新打开任务或重启 Codex。

```text
$github-project-publisher 检查当前项目，完善 README 和 Release 文案，并准备发布到 GitHub。
```

---

## English Release Notes

v0.3.1 turns the existing policy-driven publication workflow into a more verifiable safety gate. Sensitive-data review now covers reachable Git history, noreply identities must belong to the current GitHub account, structured choices are constrained by both decision semantics and runtime capability, and the project now includes behavioral evals and continuous integration. This patch also fixes a false malformed-Tagger finding when GitHub Actions exposes a tag-event checkout as a lightweight tag ref.

### Added

- Automatic enumeration and scanning of every reachable historical text blob. A sensitive value removed from the working tree still blocks publication while it remains in reachable history.
- GitHub account ownership verification for ID-based noreply addresses through `gh api user`; a syntactically valid address owned by another account no longer passes.
- Trusted CI parameters `--expected-github-id` and `--expected-github-login`, plus `--gh` for an explicit GitHub CLI path.
- Ten behavioral eval cases covering direct and implicit activation, negative activation, incomplete input, structured choices, binary confirmation, free-form input, host permission, automatic checks, and blocker behavior.
- A structured eval result schema and an optional read-only `codex exec` behavior runner.
- GitHub Actions for deterministic push/PR checks, with opt-in authenticated live Codex evals available through manual dispatch.
- Tests for Skill metadata, UI configuration, and local Markdown links.

### Changed

- Option cards now use two gates: an unresolved consequential choice must pass the semantic gate, and `request_user_input` or an equivalent tool must actually be available for the runtime gate.
- When structured input is available and the decision test passes, the Skill must call it instead of imitating a card in Markdown. When unavailable, the workflow stops before mutation and does not claim that the Skill can enable Plan mode.
- Git identity may use a personal email only after a structured choice and durable-public-metadata warning; other unapproved identities remain blockers.
- Machine-readable preflight metadata now records historical blob coverage and GitHub account verification state.
- Temporary files, local eval artifacts, and test residue are excluded from the publication set.
- Both READMEs now document runtime interaction constraints, history scanning, account verification, behavior evals, and CI.

### Security

- Removing a value from the current file no longer counts as remediating historical exposure; high-confidence matches in reachable history block publication with fully redacted location-only reporting.
- Failure to enumerate, read, or complete required scanning of a historical object blocks publication.
- Noreply verification now requires both valid syntax and an account ID/login match.

### Compatibility

- The default noreply policy now blocks Author, Committer, or annotated Tag tagger identities owned by another GitHub account, even when their noreply syntax is valid.
- Personal-email mode permits only the explicitly selected repository-local address and the verified account's noreply identity.
- Historical scanning can increase preflight time for large repositories. Binaries, images, archives, encrypted content, and proprietary formats still require manual or domain-specific review.
- Card rendering remains dependent on the Codex host, current mode, version, and account capabilities. The Skill can call an available tool but cannot inject unavailable UI controls.
- GitHub Actions may expose the current tag-event ref as a lightweight tag without Tagger metadata. Preflight now skips Tagger validation for that ref while continuing to validate genuine annotated tags strictly.

### Verification

- All 16 Python standard-library unit tests pass.
- The ten-case behavior eval corpus passes structure and coverage validation.
- Skill metadata, UI configuration, and local Markdown link checks pass.
- `git diff --check` passes.
- Strict preflight passes in a clean temporary repository with zero blockers and zero warnings.
- Reachable commit Author/Committer identities, annotated Tag taggers, and GitHub account ownership checks pass.
- This release has no user-supplied Release assets; the SHA-256 asset gate is recorded as not applicable.

### Install or upgrade

Copy the `github-project-publisher` directory into a project- or user-scoped `.codex\skills` directory, replacing the previous version, then reopen the task or restart Codex.

```text
$github-project-publisher Audit this project, draft the README and Release text, and prepare it for GitHub publication.
```
