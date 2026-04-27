# 用户须知

GodotMaker 在安装时自动执行的操作及其原因。

## 发布脚本自动行为

发布脚本（`tools/publish.py`）会在你的游戏项目目录中执行以下操作，以降低配置门槛。如果你熟悉这些工具，可以自行管理——脚本会跳过已经完成的步骤。

### Git 仓库初始化

**会发生什么：** 如果你的项目目录没有 `.git/` 文件夹，发布脚本会运行 `git init` 并创建一个初始的空提交。

**为什么：** GodotMaker 使用在隔离 git worktree 中运行的并行 Worker（`git worktree add`）。Git worktree 要求至少存在一个提交——没有提交时命令会报错：

```
fatal: not a valid object name: 'HEAD'
```

这与把代码推送到 GitHub 或任何远端服务器无关。这个提交纯粹是本地的，只是为了让并行 Worker 基础设施能够运行。

**如果我已经有 git 仓库怎么办？** 脚本会检测 `.git/` 目录并跳过 `git init`。如果已经存在提交，也会跳过。你的现有历史记录不会被修改。

**如果我不想用 git 怎么办？** 如果 worktree 创建失败，并行 Worker 会回退到顺序执行。游戏仍然会被生成，但由于 Worker 一次只能运行一个，实现过程可能会更慢。
