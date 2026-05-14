# 项目配置

`.godotmaker/config.yaml` 是每个项目独立的配置文件，用于指定使用哪个 AI 模型生成代码、哪个模型负责截图检查，以及其他你希望在不同项目间灵活调整的行为。这个文件位于项目文件夹内，因此不同的游戏可以拥有各自不同的设置。

## 文件是怎么创建的

第一次运行 `python tools/publish.py <project>` 时，发布脚本会把 GodotMaker 的默认配置复制到 `.godotmaker/config.yaml`。之后每次发布都不会覆盖这个文件——你的修改始终会被保留。

## 常用字段

以下是你最可能需要调整的字段：

**`worker_model`** — 用于编写游戏代码的 Claude 模型。Worker 承担最繁重的工作：实现系统、编写测试、修复缺口。默认值为 `opus`，因为复杂的代码生成任务需要更强的模型。如果你希望构建速度更快（但可能不那么全面），可以切换为 `sonnet`。

**`verifier_model`** — 用于运行验证检查的模型（构建是否成功编译、测试是否通过）。默认值为 `sonnet`，通常保持不变即可，除非你遇到误报失败的情况。

**`reviewer_model`** — 用于审查代码中 Godot 特定问题的模型（物理、动画、UI 常见坑）。默认值为 `sonnet`。

**`analyst_model`** — 在 `/gm-asset` 阶段检查用户提供的图片文件所使用的模型。默认值为 `sonnet`。

**`vqa_model`** — 在 `/gm-evaluate` 阶段执行视觉质量检查的 Gemini 模型（将截图与参考图进行对比）。默认值为 `gemini-2.5-flash`。如果你希望获得更高质量的视觉分析（成本也会相应提高），可以填写更新的 Gemini 模型名称。

**`asset_image_provider`** — `tools/asset_gen.py image` 在没有传 `--model` 时使用的图片生成后端。默认值为 `gemini`，因为 GodotMaker 默认要求配置 `GOOGLE_API_KEY`；只有在配置了 `XAI_API_KEY` 时才建议改为 `grok`。

**`gemini_image_model`** — `asset_gen.py image --model gemini` 使用的 Gemini 生图模型。默认值为 `gemini-3.1-flash-image-preview`（Nano Banana 2），支持框架里的 `512`、`1K`、`2K`、`4K` 尺寸预设。

**`grok_image_model`** — `asset_gen.py image --model grok` 使用的 xAI 图片模型。默认值为 `grok-imagine-image`。

**`grok_video_model`** — `asset_gen.py video` 使用的 xAI 视频模型。默认值为 `grok-imagine-video`。

默认配置文件如下：

```yaml
# GodotMaker project configuration
# Edit these values to customize behavior

# VQA model for visual quality checks (any Gemini model name)
# 默认：gemini-2.5-flash
# 可选：gemini-2.5-flash, gemini-2.0-flash, gemini-flash-latest
vqa_model: gemini-2.5-flash

# Asset generation defaults
# Gemini is the default because GOOGLE_API_KEY is required by GodotMaker.
# Grok remains available when XAI_API_KEY is configured.
asset_image_provider: gemini

# Image/video generation models
# gemini_image_model is the Nano Banana 2 image model used by --model gemini.
gemini_image_model: gemini-3.1-flash-image-preview
grok_image_model: grok-imagine-image
grok_video_model: grok-imagine-video

# Agent model configuration
# Workers use opus for complex implementation tasks
# Verifiers, reviewers, and analysts use sonnet for lighter validation work
worker_model: opus
verifier_model: sonnet
reviewer_model: sonnet
analyst_model: sonnet
```

## 如何修改配置

用任意文本编辑器打开 `.godotmaker/config.yaml`，修改冒号后面的值即可。例如，将 worker 改为使用 `sonnet` 而不是 `opus`：

```yaml
worker_model: sonnet
```

保存文件，立即生效，不需要重启任何东西。

## 修改何时生效

下一次运行 `/gm-*` 命令时，会读取文件中的最新配置。如果你在会话已经运行的情况下修改了配置，需要开启新会话才能让改动生效。

## 关于 `.claude/settings.json`

还有另一个配置文件 `.claude/settings.json`，它负责注册 Claude Code 在文件写入、会话启动、Agent 停止等事件时运行的 hook 脚本。这是框架自动管理的文件——它负责接入 GodotMaker 的安全规则，通常不需要手动修改。如果升级后 hook 停止触发，运行 `python tools/publish.py --force <project>` 可以将其重新发布为当前版本。
