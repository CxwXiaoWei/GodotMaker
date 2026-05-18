# 安装

GodotMaker 能把你用普通话描述的游戏想法，变成一个可以运行的 Godot 4 游戏。要做到这一点，需要五款软件协同工作：Godot（运行游戏的引擎）、Git（版本控制，让 AI 能安全地保存每一次改动）、Node.js（GodotMaker 用来从命令行与 Godot 通信的运行环境）、Python（负责素材生成流水线和环境检查）、以及 Claude Code（驱动整个流程的 AI 助手）。这篇指南会带你把五款软件都装好、填入图片生成所需的 API Key，并在制作第一款游戏前确认一切正常。

## 前置软件

| 工具 | 最低版本 | GodotMaker 为什么需要它 | 下载地址 |
|------|----------|------------------------|---------|
| Godot | 4.5+ | 编译并运行生成的游戏 | https://godotengine.org/download |
| Git | 2.30+ | 追踪每一个文件改动；让 AI 能并行工作而不冲突 | https://git-scm.com/downloads |
| Node.js | 18+ | 提供 `npx`，GodotMaker 用它把 Claude Code 连接到 Godot | https://nodejs.org（选 LTS 版本）|
| Python | 3.9+ | 生成美术素材、运行环境检查、驱动端到端测试 | https://python.org/downloads |
| Claude Code | 最新版 | 你输入指令的 AI 助手 | `npm install -g @anthropic-ai/claude-code` |

按照上面的链接把每款软件都装好，然后继续。

## API Key

GodotMaker 可以根据 `.godotmaker/config.yaml` 使用运行时原生图片生成，或者使用 API 后端生成图片。

默认项目使用原生 VQA 和原生资产图片生成。只有 `.godotmaker/config.yaml` 选择 API 后端时，才需要对应 API key。Claude Code 用户如果想让 Codex 负责生图，可以设置 `asset_image_model: codex`。

| Key | 什么时候需要 | 用途 |
|-----|--------------|------|
| `GOOGLE_API_KEY` 或 `GEMINI_API_KEY` | `vqa_model` 或 `asset_image_model` 使用 `gemini:<model>` | Gemini 视觉 QA 和图片生成。获取地址：https://aistudio.google.com/apikey |
| `OPENAI_API_KEY` | `vqa_model` 或 `asset_image_model` 使用 `openai:<model>` | OpenAI 视觉理解和 Images API。 |
| `XAI_API_KEY` | `asset_image_model` 或 `asset_video_model` 使用 `grok:<model>` | xAI Grok 图片或视频生成。获取地址：https://console.x.ai |
| `TRIPO3D_API_KEY` | 需要生成 GLB 模型时 | 3D 模型生成。获取地址：https://www.tripo3d.ai |

### Windows 上设置 key（PowerShell）

```powershell
[System.Environment]::SetEnvironmentVariable("GOOGLE_API_KEY", "your-key-here", "User")
```

如果需要其他可选 key，替换变量名后重复执行。执行后关闭并重新打开终端。

### macOS 或 Linux 上设置 key

```bash
export GOOGLE_API_KEY="your-key-here"
# Optional:
# export OPENAI_API_KEY="your-key-here"
# export XAI_API_KEY="your-key-here"
# export TRIPO3D_API_KEY="your-key-here"
```

## 分步安装

### 1. 克隆 GodotMaker 仓库

这一步把 GodotMaker 的工具和技能定义下载到你的电脑。只需要做一次。克隆下来的文件夹是 GodotMaker 框架本身——不是你的游戏项目。

```bash
git clone https://github.com/RandallLiuXin/GodotMaker.git
cd GodotMaker
```

### 2. 设置 Git 身份

Git 会记录每次改动是谁做的。如果你从来没设置过，运行：

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

### 3. 安装 Python 依赖

```bash
pip install -r tools/requirements.txt
```

这会安装负责图片生成、视觉质量检查和端到端测试的 Python 包。

### 4. 运行环境检查

```bash
python tools/check_env.py
```

检查工具会验证所有前置条件，并逐条打印结果：

- `[PASS]` — 没问题
- `[WARN]` — 某个可选功能缺失；游戏仍然能生成，但该功能不可用
- `[FAIL]` — 某个必要项缺失；必须修复后才能继续

继续之前，把所有 `[FAIL]` 都修好。`[WARN]` 可以暂时跳过，除非你确实需要它描述的可选功能。

## 下一步

环境检查没有 `[FAIL]` 之后，就可以开始制作第一款游戏了。前往[你的第一款游戏](first-game.md)。
