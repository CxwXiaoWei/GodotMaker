# 词汇表

GodotMaker 文档和斜线指令输出中常见术语的定义。

---

**Accept** / **Acceptance** — 流水线第八个角色，由 `/gm-accept` 触发。AI 将当前构建结果呈现给你，询问是否接受、打回重新修复，或直接停止。你的决定会以 `accept` 事件的形式记录在 `.godotmaker/stage.jsonl` 中。另见：*Milestone*、*Role*。

**Analyst** — 由 `/gm-asset` 派生的子代理，专门分析你提供的图片文件。主代理被阻止直接读取图片（防止原始像素数据耗尽上下文），因此将图片分析委托给 Analyst。Analyst 返回一份艺术风格摘要和可用资源列表。另见：*Sub-agent*。

**Asset** / **ASSETS.md** — "Asset"指游戏使用的美术或音频文件（精灵、背景、音效）。`ASSETS.md` 是列出游戏所需每项资源、由谁生成、是否已完成的规划文档。`/gm-asset` 负责生成缺失的美术资源并更新这个文件。

**Component**（ECS）— 附加到实体上的小型纯数据容器。例如 `Health` 组件可能只保存一个数字（`hp: 5`）。组件本身不含任何逻辑。另见：*ECS*、*Entity*、*System*。

**Current role** / `.godotmaker/current_role` — 每个 `/gm-*` 技能作为第一个动作写入的纯文本文件，记录当前激活的角色（如 `build`）。Hook 脚本读取这个文件来决定哪些文件写操作被允许、哪些被阻止。没有 `/gm-*` 技能运行时，文件不存在（或是上一个会话留下的过期记录，`session_start.py` 会将其清除）。另见：*Hook*、*Role*。

**ECS**（Entity-Component-System）— 所有生成的游戏代码遵循的架构。与其把数据和逻辑塞进一个大脚本，ECS 将它们分离：实体只是 ID，组件是挂在实体上的数据袋，系统是每帧遍历匹配实体的函数。这让 AI 生成的代码保持模块化，便于扩展。GodotMaker 使用 [gecs](https://github.com/csprance/gecs) 插件在 Godot 中实现 ECS。另见：*Entity*、*Component*、*System*、*gecs*。

**Entity**（ECS）— 代表游戏世界中一个"事物"（玩家、敌人、子弹）的唯一数字 ID。实体本身没有数据或行为；只有通过附加在它身上的组件才有意义。另见：*ECS*、*Component*。

**Evaluation** / **Evaluator** — 流水线第六个角色，由 `/gm-evaluate` 触发。一个独立代理以无头模式运行游戏、截图，并对照 GDD 给结果打分。评估结果写入 `.godotmaker/evaluation.json`，截图保存在 `e2e/screenshots/`。评估结果直接输入下一个角色 `/gm-fixgap`。另见：*Role*、*Visual QA*。

**Fixgap** / **GAP.md** — 第七个角色，由 `/gm-fixgap` 触发。读取评估报告，创建 `GAP.md` 列出 GDD 描述与游戏当前状态之间的每处差距，然后派发 Worker 逐一解决。修复完成后，`GAP.md` 会归档到 `.godotmaker/gaps/<n>/`。另见：*Role*、*Worker*。

**GDD**（Game Design Document，游戏设计文档）— 描述游戏全部内容的结构化文档（`GDD.md`）：游戏是什么、怎么玩、玩家做什么、胜负条件是什么。GDD 是所有后续角色反复参照的单一真相来源。由 `/gm-gdd` 生成。

**gecs** — 提供 Entity、Component、System 基础类的开源 Godot 插件，GodotMaker 在此之上构建。来源：[github.com/csprance/gecs](https://github.com/csprance/gecs)。GodotMaker 在 `config/addon_versions.json` 中锁定具体的插件版本。另见：*ECS*。

**Hook** — Claude Code 在特定事件（会话开始、文件写入前、子代理结束后等）自动运行的小型 Python 脚本。Hook 负责执行流水线规则——例如在 evaluate 角色期间阻止主代理写游戏代码，或在 `/gm-build` 已派发 Worker 但未运行 Verifier 时拒绝结束。Hook 存放在生成项目内的 `.godotmaker/hooks/`。完整列表见 `docs/hooks.md`。

**Milestone** — 从 `/gm-gdd` 到 `/gm-finalize` 的一次完整流水线通关。一个里程碑完成后，可以重新运行 `/gm-gdd` 开启下一个，添加功能或调整方向。`/gm-scaffold` 是每个项目只执行一次的步骤，不在里程碑之间重复。

**PLAN.md** — 由 `/gm-gdd` 生成的任务列表。它将 GDD 分解为一个个具体实现任务，每项任务都有状态字段（`pending` / `in_progress` / `completed` / `verified`）。`/gm-build` 通过为每个任务派发 Worker 来逐一推进。Hook `stage_reminder.py` 会阻止 `/gm-build` 在所有任务都标记为 `verified` 之前结束。

**Reviewer** — 一种子代理，以及一套 8 个专项技能（`physics`、`animation`、`ui`、`tilemap`、`navigation`、`shader`、`audio`、`particles`）。Worker 实现任务、Verifier 测试完成后，Reviewer 对代码进行检查，比对每个技能的 `gotchas.md` 和 `checklist.md` 中记录的 Godot 特有坑。发现的新问题会作为新任务反馈到 `PLAN.md`。另见：*Sub-agent*、*Worker*、*Verifier*。

**Role** — GodotMaker 流水线中九个有明确职责的步骤之一。每个角色对应一条 `/gm-*` 斜线指令，并对可以读写哪些文件有明确的范围限制。Role 取代了早期的"stage"概念（见下文 *Stage vs Role*）。九个角色按顺序为：`scaffold`、`gdd`、`asset`、`build`、`verify`、`evaluate`、`fixgap`、`accept`、`finalize`。

**SCENES.md** — 由 `/gm-gdd` 生成的规划文档，列出游戏需要的每个 Godot 场景、包含的内容以及场景之间的关系。build 角色在实现场景树结构时会参考这份文档。

**Skill**（Claude Code 技能）— 一个给 Claude Code 提供特定工作指令的 Markdown 文件（`SKILL.md`）。GodotMaker 提供 9 个角色技能（`/gm-*` 指令）、12 个辅助技能（参考文档和助手工具）以及 8 个审查员技能。技能被部署到生成项目内的 `.claude/skills/`。用户通过输入斜线指令来调用角色技能；辅助技能和审查员技能由角色技能在内部调用。

**Stage vs Role** — "Stage"是 GodotMaker 早期对流水线步骤的称呼，"8 阶段流水线"描述的是最初的架构。流水线已被重新设计为 9 个基于角色的指令，没有中央协调器。"stage"这个词可能还出现在部分文件名中（如 `stage_schemas.json`、`stage.jsonl`）和旧文档里，但今后的规范术语是"role"。另见：*Role*。

**stage.jsonl** — 位于 `.godotmaker/stage.jsonl` 的只追加日志文件。每当一个 `/gm-*` 角色成功完成时，它追加一行 JSON：`{"role": "<name>", "ts": "<iso-timestamp>"}`。`check_stage_prerequisites.py` Hook 读取此文件，确认所需的早期角色已完成，然后才允许新角色开始。"jsonl"表示每行是一个独立的合法 JSON 对象。

**STRUCTURE.md** — 由 `/gm-gdd` 生成的规划文档，描述生成项目的文件夹布局：哪些目录存在、每个目录放什么类型的文件、源码树如何组织。

**Sub-agent** — 主角色代理派生的 AI 代理，用于并行处理特定的工作内容。子代理在隔离的 git worktree 中运行，互不干扰。四种子代理类型：*Worker*、*Verifier*、*Reviewer*、*Analyst*。

**System**（ECS）— 每帧遍历所有拥有特定组件组合的实体的函数（或 GDScript 类）。例如，`MovementSystem` 可能遍历所有同时拥有 `Velocity` 组件和 `Position` 组件的实体，每帧更新其位置。System 包含所有游戏逻辑。另见：*ECS*、*Entity*、*Component*。

**TOC.md** — 由 `/gm-gdd` 生成的目录文档，列出所有规划文档及其位置。它提供每个里程碑开始时项目内容的快速概览。

**Verifier** — 运行无头 Godot 构建和 Worker 编写的单元测试，然后报告是否通过的子代理。Verifier 还会执行"对抗性探测"——针对边界情况和错误处理的定向测试。如果验证失败，问题返回给 Worker。另见：*Sub-agent*、*Worker*、*Reviewer*。

**Visual QA** / **VQA** — 将运行中的游戏截图与参考图像或一组书面标准进行比对的过程。`/gm-evaluate` 使用 `visual-qa` 技能（由 Gemini 驱动）对照 GDD 描述和 `/gm-asset` 生成的每个场景参考图，为每个场景打分。另见：*Evaluation*。

**Worker** — 实现一个游戏任务的子代理：编写 GDScript 代码、单元测试和端到端测试，然后返回一份结构化报告。Worker 在隔离的 git worktree 中运行。Worker 完成后，必须由 Verifier 和 Reviewer 先后完成验收，才会开始下一个任务。另见：*Sub-agent*、*Verifier*、*Reviewer*、*Worktree*。

**Worktree** — 允许多个工作目录共享同一个仓库的 git 功能。GodotMaker 用 worktree 让并行子代理各自拥有独立的文件夹来写文件，互不冲突。Worktree 要求仓库至少有一个提交，这也是 `/gm-scaffold` 总是创建初始提交的原因。另见：*Sub-agent*。
