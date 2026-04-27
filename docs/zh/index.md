# GodotMaker

**用一句话描述你想做的游戏，得到一个完整可运行的 Godot 4 项目。**

GodotMaker 接收你的想法——用日常语言写下来——然后生成可运行的游戏代码、美术资源、测试和质量检查。你用九条斜线指令驱动整个流程；框架在中间帮你把好每一关。

## 你能得到什么

- **描述，而不是配置** — 写一段白话需求说明，框架自动规划、搭架、写代码
- **默认带测试** — 单元测试（gdUnit4）和端到端测试与游戏代码同步生成，不是事后打补丁
- **提前发现 Godot 特有的 bug** — 八个领域审查员（物理、动画、UI、地图块、导航、着色器、音频、粒子）在你看到构建结果前就标记出常见坑
- **内置视觉质量检查** — 自动截图 + AI 视觉评估，确认游戏"看起来对"，而不只是"编译通过"
- **一致的 ECS 结构** — 所有生成的游戏逻辑都遵循 Entity-Component-System 架构（通过 [gecs](https://github.com/csprance/gecs)），代码随规模增长依然可预测
- **你始终掌控节奏** — 每一步都是一条斜线指令；你决定何时开始下一步，随时可以停，随时可以继续

## 第一次用？从这三页开始

1. [安装](wiki/01-getting-started/installation.md) — 需要什么环境，怎么配置
2. [做你的第一个游戏](wiki/01-getting-started/first-game.md) — 从头到尾跑一遍全部九条指令的演练
3. [它是怎么工作的](wiki/02-concepts/how-it-works.md) — 那些指令背后，框架实际在做什么

## 其他快速入口

- [9 个角色](wiki/02-concepts/the-9-roles.md) — 每条 `/gm-*` 指令做什么
- [故障排查](wiki/04-troubleshooting/common-problems.md) — 常见问题的解决方法
- [FAQ](wiki/08-reference/faq.md)
- [参与贡献](wiki/07-contributing/development-setup.md)
- [GitHub 仓库](https://github.com/RandallLiuXin/GodotMaker)

## 项目状态

- 当前版本：见 [`VERSION`](https://github.com/RandallLiuXin/GodotMaker/blob/main/VERSION) 和 [`CHANGELOG.md`](https://github.com/RandallLiuXin/GodotMaker/blob/main/CHANGELOG.md)
- 路线图：[`ROADMAP.md`](https://github.com/RandallLiuXin/GodotMaker/blob/main/ROADMAP.md)
