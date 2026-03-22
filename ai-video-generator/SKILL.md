---
name: ai-video-generator
description: 根据脚本自动生成短视频。使用火山引擎Seedance 1.5 pro生成视频片段（支持有声视频），FFmpeg拼接成完整视频。当用户说"生成视频"、"AI视频制作"、"脚本转视频"、"制作短视频"，或提供脚本JSON要求生成视频时触发。支持文生视频、图生视频、首尾帧连续生成。
---

# AI视频生成

根据脚本自动生成短视频。

## 快速开始

基础工作流（文生视频）：

```bash
# 1. 安装依赖
pip install requests

# 2. 配置API Key（在项目根目录的config.js中）
# ARK_API_KEY: 'your_api_key'

# 3. 批量生成视频
python scripts/generate_all.py --script script.json --output-dir ./clips

# 4. 拼接视频
./scripts/concat_videos.sh ./clips output.mp4
```

带首尾帧的工作流（适合有产品图片的场景）：

```bash
# 1. 生成首帧（可选，如果已有产品图片可跳过）
python scripts/generate_keyframes.py \
  --prompt "产品特写展示" \
  --first-frame \
  --output-dir ./keyframes

# 2. 批量生成视频（使用首帧）
python scripts/generate_all.py \
  --script script.json \
  --first-frame ./keyframes/first_frame.jpg \
  --output-dir ./clips

# 3. 拼接视频
./scripts/concat_videos.sh ./clips output.mp4
```

脚本会自动从 `config.js` 读取 `ARK_API_KEY`。

## 脚本列表

| 脚本 | 用途 |
|------|------|
| `generate_video.py` | 生成单个视频片段 |
| `generate_all.py` | 批量生成+尾帧接首帧 |
| `generate_keyframes.py` | 生成首尾帧图片 |
| `concat_videos.sh` | FFmpeg拼接视频 |

## 单个视频生成

```bash
python scripts/generate_video.py \
  --prompt "职场女性对着镜头说：'这3个技巧...'，表情认真，特写镜头" \
  --duration 5 \
  --output clip.mp4

参数:
  --prompt, -p     视频描述 (必填)
  --duration, -d   时长4-12秒，默认5
  --first-frame    首帧图片URL
  --resolution     480p/720p/1080p，默认720p
  --ratio          16:9/9:16/1:1，默认16:9
  --no-audio       不生成音频
  --output, -o     输出文件路径
```

## 批量视频生成

```bash
python scripts/generate_all.py \
  --script script.json \
  --output-dir ./clips \
  --resolution 720p \
  --ratio 16:9

参数:
  --script, -s     脚本JSON文件 (必填)
  --output-dir     输出目录，默认./clips
  --resolution     分辨率
  --ratio          宽高比
  --no-audio       不生成音频
  --first-frame    首帧图片URL或路径（用于第一个片段）
```

## 首尾帧生成

使用Seedream 4.5生成首尾帧图片，适合有产品图片需求的场景。

```bash
# 生成首帧
python scripts/generate_keyframes.py \
  --prompt "产品展示，清晰的产品特写" \
  --first-frame \
  --output-dir ./keyframes

# 生成尾帧
python scripts/generate_keyframes.py \
  --prompt "引导关注，行动号召画面" \
  --last-frame \
  --output-dir ./keyframes

# 基于参考图生成
python scripts/generate_keyframes.py \
  --prompt "产品展示" \
  --reference product.jpg \
  --first-frame \
  --output-dir ./keyframes

参数:
  --prompt, -p     图片描述 (必填)
  --reference, -r  参考图片URL或路径
  --size, -s       图片尺寸，默认2560x1440（16:9）
  --first-frame    生成首帧
  --last-frame     生成尾帧
  --output-dir     输出目录，默认./keyframes
```

## 脚本JSON格式

基础格式：

```json
{
  "scenes": [
    {"prompt": "职场女性对着镜头说：'这3个技巧...'，特写", "duration": 4},
    {"prompt": "职场女性继续说：'你每天都在加班？'，中景", "duration": 4},
    {"prompt": "职场女性讲解第一个技巧，手势自然，中景", "duration": 12},
    {"prompt": "职场女性讲解第二个技巧，中景", "duration": 12},
    {"prompt": "职场女性讲解第三个技巧，中景", "duration": 12},
    {"prompt": "职场女性说：'其实最重要的是...'，特写", "duration": 6},
    {"prompt": "职场女性微笑说：'关注我...'，挥手，中景", "duration": 6}
  ],
  "resolution": "720p",
  "ratio": "16:9",
  "generate_audio": true
}
```

带音画同步的格式（推荐）：

```json
{
  "scenes": [
    {"prompt": "职场女性对着镜头说："这3个技巧，90%的人都不知道"，表情认真，特写镜头", "duration": 4},
    {"prompt": "职场女性继续说："你每天都在加班？其实效率比时间更重要"，中景", "duration": 5},
    {"prompt": "职场女性讲解第一个技巧说："第一，学会时间分块管理"，手势自然，中景", "duration": 8},
    {"prompt": "职场女性讲解第二个技巧说："第二，优先处理重要不紧急的事"，中景", "duration": 8},
    {"prompt": "职场女性讲解第三个技巧说："第三，每天留出30分钟深度思考"，中景", "duration": 8},
    {"prompt": "职场女性说："其实最重要的不是管理时间，而是管理精力"，表情严肃，特写", "duration": 6},
    {"prompt": "职场女性微笑说："关注我，每天分享一个职场技巧"，挥手，中景", "duration": 5}
  ],
  "resolution": "720p",
  "ratio": "16:9",
  "generate_audio": true
}
```

带首帧的格式（适合有产品图片的场景）：

```json
{
  "first_frame": "https://example.com/product.jpg",
  "scenes": [
    {"prompt": "产品特写展示，清晰的产品细节", "duration": 5},
    {"prompt": "产品使用场景，用户正在使用产品", "duration": 8},
    {"prompt": "产品优势展示，突出核心卖点", "duration": 10},
    {"prompt": "引导关注，行动号召画面", "duration": 5}
  ],
  "resolution": "720p",
  "ratio": "16:9",
  "generate_audio": true
}
```

## 视频拼接

```bash
# 自动拼接clips目录下的视频
./scripts/concat_videos.sh ./clips output.mp4

# 手动拼接
cd ./clips
ffmpeg -f concat -safe 0 -i filelist.txt -c copy output.mp4
```

## API参数

| 参数 | 值 | 说明 |
|------|-----|------|
| model | doubao-seedance-1-5-pro-251215 | Seedance 1.5 pro |
| resolution | 480p / 720p / 1080p | 视频分辨率 |
| ratio | 16:9 / 9:16 / 1:1 / adaptive | 宽高比 |
| duration | 4-12秒 | 视频时长 |
| generate_audio | true / false | **音画同步**（仅1.5 pro支持）<br>true: 自动生成与画面同步的人声、音效、背景音乐<br>false: 无声视频<br>**默认值: true** |

## Prompt示例

```
口播：职场女性对着镜头说："这3个技巧..."，表情认真，特写镜头
展示：电脑屏幕特写，显示软件界面，鼠标点击操作
结尾：职场女性微笑说："关注我..."，挥手，中景
```

## 音画同步提示

**Seedance 1.5 pro 支持自动生成与画面同步的音频**，包括：
- 人声对话
- 环境音效
- 背景音乐

**Prompt优化建议**：
- 将对话内容放在**双引号**内，优化音频生成效果
- 示例：`男人叫住女人说："你记住，以后不可以用手指指月亮。"`
- 描述环境音效：`海浪拍打礁石的声音，海鸥鸣叫`
- 描述背景音乐：`轻快的钢琴背景音乐`
