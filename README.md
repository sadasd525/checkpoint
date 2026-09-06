# Checkpoint

一个GitHub 的 Codex skill，用三个显式操作管理项目工作：

```text
$checkpoint save
$checkpoint resume
$checkpoint publish
```

- `save`（保存进度）：在当前项目根目录的 `.project-checkpoint/` 中保存文件夹名称、规范路径、时间、Git 状态、已完成内容、当前步骤与下一步。
- `resume`（恢复进度）：只读取当前项目自己的检查点，核对路径与 Git remote 后继续工作。
- `publish`（上传 GitHub）：提交当前项目代码，并创建或使用已经验证为 **PRIVATE** 的 GitHub 仓库进行推送。

## 安装

把本目录复制到项目级 `.agents/skills/checkpoint/`，或个人技能目录
`~/.agents/skills/checkpoint/`。重启 Codex 后，可通过 `/skills` 选择，
也可以直接输入上面的 `$checkpoint ...`。

本技能采用显式调用策略，不会因为普通对话里的“继续”而读取旧进度。Skill
本身不会注册真正的 `/checkpoint` 斜杠命令；`/skills` 是终端里的技能菜单，
`$checkpoint` 是终端和 IDE 中直接指定本技能的方式。

## 隔离方式

每个项目的状态只保存在自身目录：

```text
<project-root>/.project-checkpoint/
├── PROJECT.md
└── CHECKPOINT.md
```

恢复和覆盖保存前都会检查 canonical project root；如果是同一仓库的另一份
checkout，则还需匹配去除认证信息后的 Git remote，并核对实际工作区。技能不会
扫描相邻项目或全局检查点，因此不同文件夹之间不会串档。

## GitHub 发布要求

需要本机已经安装 `git` 和 GitHub CLI `gh`，并由用户通过 `gh auth login` 完成
登录。`publish` 默认使用当前文件夹名创建私有仓库；已有 `origin` 时，只允许推送
到经 `gh` 验证为 `PRIVATE` 的 GitHub 仓库。

发布前会检查疑似密钥文件和异常大文件。它不会自动公开仓库、替换远程、改写历史、
force push、保存 token，或把一个同名但身份不明的远程当作当前项目。本地的
`.project-checkpoint/` 默认不会作为代码提交到 GitHub。

## 文件

- `SKILL.md`：三个操作与安全边界。
- `scripts/project_context.py`：只读识别当前项目、文件夹、时间及 Git 状态。
- `references/checkpoint-format.md`：进度文件格式。
- `references/github-publish.md`：私有 GitHub 发布流程。
- `agents/openai.yaml`：技能列表中的显示信息与显式调用策略。
- `.gitignore`：排除 Python 缓存和本地进度记录。
- `LICENSE`：MIT 许可证。

## 本地验证

```text
python scripts/project_context.py --json
python <skill-creator>/scripts/quick_validate.py .
```

辅助脚本仅收集只读上下文；检查点写入和 GitHub 操作由调用该技能的 Codex agent
按 `SKILL.md` 执行。
