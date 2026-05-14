# 素材工具

GodotMaker 通过几个小型 Python 辅助脚本生成美术资源。`/gm-asset` 会自动调用它们——但如果你需要重新生成某个文件或试验不同参数，也可以手动运行。

## asset_gen.py

`asset_gen.py` 是主要的图片和 3D 模型生成器，支持两种图片提供商和一种 3D 模型服务。

**图片提供商：**

| 提供商 | 单张价格 | 适合场景 |
|----------|---------------|---------|
| xAI Grok | 2 美分（仅 1K 或 2K） | 速度快，适合大多数精灵和 UI 元素 |
| Google Gemini | 5–15 美分（512 到 4K） | 提示词跟随更精确，适合细节丰富或需要编辑的图片 |

Gemini 需要 `GOOGLE_API_KEY`，这是 GodotMaker 默认要求配置的密钥。Grok 需要可选的 `XAI_API_KEY`。要设置 `/gm-asset` 默认使用哪个提供商，请在 [`../06-configuration/project-config.md`](../06-configuration/project-config.md) 中配置 `asset_image_provider`。

### 生成图片

```bash
python tools/asset_gen.py image \
  --prompt "top-down pixel art player character, blue outfit, 64x64, transparent background" \
  -o assets/sprites/player.png
```

改用 Grok：

```bash
python tools/asset_gen.py image \
  --prompt "top-down pixel art player character, blue outfit, 64x64, transparent background" \
  --model grok \
  --size 1K \
  -o assets/sprites/player.png
```

编辑现有图片（图生图）：

```bash
python tools/asset_gen.py image \
  --prompt "add a glowing aura around the character" \
  --image assets/sprites/player.png \
  -o assets/sprites/player_glow.png
```

**常用选项：**

| 选项 | 默认值 | 说明 |
|--------|---------|-------|
| `--prompt` | （必填） | 描述你想要的内容 |
| `--model` | 项目配置 | `gemini` 或 `grok`；覆盖 `asset_image_provider` |
| `--size` | `1K` | Grok：`1K`、`2K`；Gemini：`512`、`1K`、`2K`、`4K` |
| `--aspect-ratio` | `1:1` | 支持多种比例，运行 `--help` 查看全部选项 |
| `--image` | 无 | 提供参考图片进行编辑 |
| `-o` | （必填） | 输出文件路径 |

### 设置预算上限

你可以设置总消费上限，避免意外超支：

```bash
python tools/asset_gen.py set_budget 500
```

这会设置 500 美分（5.00 美元）的限额，记录在 `assets/budget.json` 中。任何生成命令在调用 API 之前，如果发现剩余预算不足，会直接报错退出。

### 生成 3D 模型

`glb` 子命令通过 Tripo3D 将 PNG 图片转换为 3D 模型（`.glb` 文件）。需要 `TRIPO3D_API_KEY`，仅适用于 3D 游戏。

```bash
python tools/asset_gen.py glb \
  --image assets/sprites/tree.png \
  -o assets/models/tree.glb
```

费用约为每个模型 40–50 美分，具体取决于 `--quality` 预设（`default` 或 `high`）。

## rembg_matting.py

`rembg_matting.py` 用于去除图片的纯色背景，输出带透明背景的 PNG 文件。当你有一张渲染在纯色背景上的精灵图，需要抠图后放入场景时，就用这个工具。

```bash
# 单张图片，自动选择最佳处理方式
python tools/rembg_matting.py assets/sprites/enemy_raw.png -o assets/sprites/enemy.png

# 批量处理：处理文件夹中的所有 PNG
python tools/rembg_matting.py --batch raw_frames/ -o clean_frames/

# 生成预览图，方便使用前确认效果
python tools/rembg_matting.py assets/sprites/enemy_raw.png --preview
```

工具使用神经网络（BiRefNet）识别主体，结合颜色抠图清理边缘。大多数图片能自动选择合适方案；如果自动结果不够干净，可以用 `-m trust`、`-m adapt` 或 `-m color` 强制指定模式。

如果有支持 CUDA 的 NVIDIA GPU，会自动启用 GPU 加速。在 CPU 上运行较慢，但同样可用。

## tripo3d.py

`tripo3d.py` 是 `asset_gen.py glb` 内部使用的 Tripo3D API 客户端。通常不需要直接调用它——请使用 `asset_gen.py` 的 `glb` 子命令。需要 `TRIPO3D_API_KEY`。

## 手动调用这些脚本的场景

大多数情况下不需要直接运行这些脚本。`/gm-asset` 会根据你的 `ASSETS.md` 自动调度它们，并填入正确的提示词和输出路径。

需要手动调用的主要场景：

- 你想用调整过的提示词重新生成某一个特定素材。
- 在完整运行 `/gm-asset` 之前，你想先试验不同的尺寸、提供商或宽高比。
- 你拿到了外部提供的美术素材，需要用 `rembg_matting.py` 去除背景。

如果你想更新 `/gm-evaluate` 用于对比的视觉目标，请重新运行 `/gm-asset`，而不是直接修改已生成的图片。手动编辑的图片在下次 `/gm-asset` 运行时会被覆盖。
