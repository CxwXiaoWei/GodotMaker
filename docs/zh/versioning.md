# 版本控制与升级

GodotMaker 的版本追踪方式，以及版本之间的升级处理机制。

## 版本方案

GodotMaker 使用[语义化版本](https://semver.org/)：`MAJOR.MINOR.PATCH`

| 级别 | 含义 | 示例 | 升级行为 |
|------|------|------|----------|
| **PATCH** | Bug 修复，无功能变化 | `0.3.0 → 0.3.1` | 自动继续，仅显示提示信息 |
| **MINOR** | 新功能或行为变化 | `0.3.0 → 0.4.0` | 显示 Changelog，需要确认 |
| **MAJOR** | 破坏性变更，可能需要迁移 | `0.x → 1.x` | 强烈警告，需要确认 |

## 版本文件位置

| 文件 | 位置 | 用途 |
|------|------|------|
| `VERSION` | GodotMaker 仓库根目录 | 当前版本的唯一真相来源 |
| `.godotmaker/version` | 目标游戏项目 | 记录上次发布的版本 |
| `CHANGELOG.md` | GodotMaker 仓库根目录 | 每个版本的人类可读变更记录 |
| `migrations/` | GodotMaker 仓库根目录 | 版本迁移脚本 |

## 发布与升级

### 全新安装

```bash
python tools/publish.py /path/to/my-game
```

目标中不存在版本记录——发布直接进行，并将版本号写入 `.godotmaker/version`。

### 升级（重新发布到已有项目）

```bash
python tools/publish.py /path/to/my-game
```

发布脚本将源码的 `VERSION` 与目标的 `.godotmaker/version` 进行比对，根据升级级别执行不同行为：

| 级别 | 行为 |
|------|------|
| **PATCH** | 自动继续，不运行迁移脚本 |
| **MINOR** | 显示 Changelog，询问确认，然后运行迁移脚本 |
| **MAJOR** | 阻止增量迁移，需要 `--force` 才能进行干净的重新初始化 |

### 版本迁移

MINOR 升级可能包含自动修复目标项目兼容性问题的迁移脚本。迁移脚本存放在 `migrations/{old}_to_{new}/`，按排序顺序运行。

示例：从 0.2.0 升级到 0.4.0 时运行：
```
migrations/0.2_to_0.3/001_xxx.py
migrations/0.2_to_0.3/002_yyy.py
migrations/0.3_to_0.4/001_track_hooks.py
migrations/0.3_to_0.4/002_track_stage_schemas.py
```

如果某个迁移脚本失败，整个链条中止，发布以错误退出。目标项目可能处于部分迁移状态——修复问题后重新运行发布，或使用 `--force` 做干净安装。

迁移脚本也可以单独运行用于测试：
```bash
python tools/migrate.py /path/to/my-game --from 0.3.0 --to 0.4.0
```

### MAJOR 升级

MAJOR 版本变更意味着无法通过增量迁移处理的破坏性变更。`publish.py` 拒绝跨 MAJOR 边界升级，除非使用 `--force`，该选项会执行干净的重新初始化。

全量重建会清除所有框架管理的内容：
- `.claude/skills/`、`.claude/agents/`、`.claude/config/`、`.claude/templates/`
- `.godotmaker/hooks/`、`.godotmaker/stage_schemas.json`
- `.godotmaker/state.json`、`.godotmaker/metrics*.jsonl`
- `tools/`
- `.claude/settings.json`（强制覆盖）

保留（用户配置）：
- `CLAUDE.md`、`.claude/godotmaker.yaml`、`.godotmaker/config.yaml`

上一个 MAJOR 版本的所有迁移脚本在发布时删除——不会带入下一版本。

### 降级

降级（如 `0.4.0 → 0.3.0`）默认被阻止。使用 `--force` 可以绕过限制：

```bash
python tools/publish.py --force /path/to/my-game
```

### 重新发布相同版本

重新发布相同版本始终允许，在开发期间拾取本地变更时很有用。

## 会话中的版本显示

在已发布的项目中启动 Claude Code 会话时，`session_start.py` Hook 读取 `.godotmaker/version` 并将 `[GodotMaker vX.Y.Z]` 注入会话上下文。这让当前角色技能和用户都能知道部署的是哪个框架版本。

## 发布新版本的工作流程

1. 在 GodotMaker 仓库中做出你的修改
2. 如果修改需要迁移（MINOR 版本升级），在 `migrations/{old}_to_{new}/` 添加迁移脚本——详见 `migrations/README.md`
3. 更新 `CHANGELOG.md`——在顶部添加新的 `## [X.Y.Z]` 分区
4. 更新 `VERSION`——改为新版本号
5. 提交并（可选）打标签：
   ```bash
   git add VERSION CHANGELOG.md migrations/
   git commit -m "release: vX.Y.Z"
   git tag vX.Y.Z
   ```
6. 发布到目标项目：
   ```bash
   python tools/publish.py /path/to/my-game
   ```

## 升级时会覆盖什么

每次发布都会覆盖：

| 目录 | 内容 |
|------|------|
| `.claude/skills/` | 所有技能（从 core + reviewer 展平） |
| `.claude/agents/` | 代理定义（worker、verifier、reviewer、analyst） |
| `.godotmaker/hooks/` | 所有 Hook 脚本 |
| `.claude/config/` | 配置文件（仅 `--force` 时覆盖 settings.json） |
| `.claude/templates/` | 文档模板 |
| `tools/` | Python 工具（check_project、check_env 等） |

以下**不会**被覆盖（仅在全新安装时创建）：

| 文件 | 原因 |
|------|------|
| `CLAUDE.md` | 用户可能已自定义 |
| `.claude/settings.json` | 用户 Hook 配置（仅 `--force` 时覆盖） |
| `.claude/godotmaker.yaml` | 主机特定路径 |
| `.godotmaker/config.yaml` | 项目特定设置 |

## 关于 addon_versions.json 的说明

`config/addon_versions.json` 追踪 Godot 插件版本（gecs、gdUnit4 等）——这与 GodotMaker 自身的版本是分开的。插件版本按 Godot 引擎版本锁定，独立管理。
