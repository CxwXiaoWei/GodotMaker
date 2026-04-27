# GodotMaker Wiki

GodotMaker 接收你对游戏的白话描述，将其转化为完整可运行的 Godot 4 项目——代码、美术、测试和质量检查一步到位。你用九条斜线指令驱动整个流程；框架在中间帮你把好每一关。

## 第一次来？先看这三页

1. [安装](01-getting-started/installation.md) — 需要什么环境，怎么配置
2. [做你的第一个游戏](01-getting-started/first-game.md) — 从头到尾跑一遍全部九条指令的演练
3. [它是怎么工作的](02-concepts/how-it-works.md) — 那些指令背后，框架实际在做什么

## Wiki 分区

| 分区 | 什么时候看 |
|------|-----------|
| [快速上手](01-getting-started/installation.md) | 第一次配置 GodotMaker，或新建项目 |
| [核心概念](02-concepts/how-it-works.md) | 想理解 9 角色流水线、ECS 和设计选择 |
| [技能系统](03-skills/skill-system.md) | 了解角色技能、辅助技能、审查员技能分别做什么 |
| [故障排查](04-troubleshooting/common-problems.md) | 指令卡住、被拦截或行为异常——在这里找解法 |
| [工具](05-tools/publish.md) | `publish.py`、`check_env.py`、`check_project.py` 及资源工具参考 |
| [配置](06-configuration/project-config.md) | 每个项目的偏好设置、主机路径、插件版本锁定 |
| [参与贡献](07-contributing/development-setup.md) | 想新增技能、Hook 或工具，或发布版本 |
| [参考](08-reference/glossary.md) | 词汇表、FAQ，以及指向 Changelog 的链接 |

## GodotMaker 能为你做什么

| 能力 | 对你意味着什么 |
|------|--------------|
| **描述，而不是配置** | 写一段白话需求说明，框架自动规划、搭架、写代码 |
| **默认带测试** | 单元测试（gdUnit4）和端到端测试与游戏代码同步生成，不是事后打补丁 |
| **提前发现 Godot 特有的 bug** | 八个领域审查员（物理、动画、UI、地图块、导航、着色器、音频、粒子）在你看到构建结果前就标记出常见坑 |
| **内置视觉质量检查** | 自动截图 + AI 视觉评估，确认游戏"看起来对"，而不只是"编译通过" |
| **一致的 ECS 结构** | 所有生成的游戏逻辑都通过 `gecs` 遵循 Entity-Component-System 架构，代码结构可预测 |
| **你始终掌控节奏** | 每一步都是一条斜线指令；你决定何时开始下一步，随时可以停，随时可以继续 |

## 项目状态

- 当前版本：见 [`VERSION`](https://github.com/RandallLiuXin/GodotMaker/blob/main/VERSION) 和 [`CHANGELOG.md`](https://github.com/RandallLiuXin/GodotMaker/blob/main/CHANGELOG.md)
- 下一版本计划：[`docs/update/next.md`](../update/next.md)
- 路线图：[`ROADMAP.md`](https://github.com/RandallLiuXin/GodotMaker/blob/main/ROADMAP.md)

## 快速链接

- [GodotMaker 仓库](https://github.com/RandallLiuXin/GodotMaker)
- [gecs — ECS 框架](https://github.com/csprance/gecs)
- [gdUnit4 — 测试框架](https://github.com/MikeSchulze/gdUnit4)
- [godot-mcp — 运行时调试](https://github.com/Coding-Solo/godot-mcp)
