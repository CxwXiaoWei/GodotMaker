# 发版流程

GodotMaker 使用语义版本控制。每次发版遵循一份简短的清单；本页是该清单的摘要。完整清单在 `docs/contributing/release-checklist.md`。

关于版本方案细节以及 `publish.py` 如何处理目标项目的升级，请参阅 [../../versioning.md](../../versioning.md)。

---

## 何时升级哪个版本号

| 级别 | 场景 | 示例 |
|-------|------|---------|
| PATCH | 不改变行为的 bug 修复 | `0.4.0 → 0.4.1` |
| MINOR | 新功能或行为变更（向后兼容） | `0.4.0 → 0.5.0` |
| MAJOR | 破坏性变更，无法通过增量迁移解决 | `0.x → 1.0.0` |

`publish.py` 在 PATCH 升级时自动继续，在 MINOR 升级时弹出确认提示，在 MAJOR 升级时要求 `--force`。

---

## next.md 工作流

贡献者从不直接编辑 `CHANGELOG.md`。每个 Pull Request 都需要在 `docs/update/next.md` 的适当分类下至少添加一条记录：

```markdown
## Added
- 新增内容的简要说明 (#123) — @author

## Changed
- 发生了什么变化以及原因 (#124) — @author

## Fixed
- 修复了什么问题 (#125) — @author

## Removed
- 删除了什么内容 (#126) — @author
```

分类名称遵循 [Keep a Changelog](https://keepachangelog.com/) 规范。如果四个标准分类都不合适，可以新增一个。

发版时，`next.md` 会被归档，并从模板创建新的空 `next.md`。贡献者立即开始向新的 `next.md` 添加下一批变更记录。这意味着 `CHANGELOG.md` 每次发版只由负责发版的人修改一次。

---

## 执行发版

高层次清单。遵循 `docs/contributing/release-checklist.md` 中的完整步骤：

1. **合并所有待发布的 PR。** 确认 `next.md` 中包含所有 PR 的记录。

2. **归档 next.md。** 将 `docs/update/next.md` 重命名为 `docs/update/vX.Y.Z.md`，然后从该文件顶部的模板创建新的 `docs/update/next.md`。

3. **更新 CHANGELOG.md。** 在文件开头插入新章节：

   ```markdown
   ## [X.Y.Z] — YYYY-MM-DD

   ### Added
   - （来自 next.md 的条目）

   ### Changed / Fixed / Removed
   - ...
   ```

4. **升级 VERSION。** 将新版本号写入仓库根目录的 `VERSION` 文件。这是唯一的真实来源。

5. **添加迁移脚本**（仅限 MINOR）。如果任何变更需要更新现有游戏项目的文件，在 `migrations/{old}_to_{new}/` 下添加迁移脚本。脚本有编号，由 `tools/migrate.py` 按序执行。脚本格式见 `migrations/README.md`。

6. **提交并打标签。**

   ```bash
   git add VERSION CHANGELOG.md docs/update/ migrations/
   git commit -m "release: vX.Y.Z"
   git tag vX.Y.Z
   ```

7. **发布到测试项目**，确认没有问题：

   ```bash
   python tools/publish.py /path/to/test-game
   ```

---

## 迁移脚本

每个 MINOR 版本可能附带迁移脚本，自动修复现有游戏项目中的兼容性问题。脚本存放在 `migrations/{old}_to_{new}/` 下，例如：

```
migrations/0.3_to_0.4/001_track_hooks.py
migrations/0.3_to_0.4/002_track_stage_schemas.py
```

当 `publish.py` 检测到 MINOR 升级时，`tools/migrate.py` 会按字母序依次运行这些脚本。某个脚本失败时，迁移链中止，publish 以错误退出。此时目标项目可能处于部分迁移状态——修复问题后重新运行 publish 即可继续，或者使用 `--force` 进行干净安装。

在 MAJOR 版本发布时，上一个 MAJOR 版本的所有迁移脚本都会被删除，不会延续——MAJOR 升级改用 `--force` 进行干净的重新初始化。
