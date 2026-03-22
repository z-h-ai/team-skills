---
name: video-analyzer
description: 从短视频中提取结构、台词、节奏，生成可复用脚本模板。使用火山引擎视频理解API分析视频内容。当用户说"拆解视频"、"分析视频结构"、"提取脚本模板"、"视频拆解"，或提供MP4/AVI/MOV视频文件要求分析时触发。输出黄金3秒、冲突设置、内容展开、反转高潮、CTA引导的完整结构化脚本。
---

# 短视频拆解分析

从爆款视频提取可复用脚本模板。

## 限制

- 时长：≤60秒
- 大小：≤50MB（URL/Base64）或≤512MB（Files API）
- 格式：MP4、AVI、MOV

## 快速开始

```bash
# 1. 安装依赖
pip install volcengine-python-sdk[ark] requests

# 2. 配置API Key（在项目根目录的config.js中）
# ARK_API_KEY: 'your_api_key'
# SPEECH_APP_KEY: 'your_speech_app_key'  # 可选，用于音频转录
# SPEECH_ACCESS_KEY: 'your_speech_access_key'  # 可选，用于音频转录

# 3. 分析视频（仅视觉分析）
python scripts/analyze_video.py video.mp4 --output result.json

# 4. 分析视频（包含音频转录）
python scripts/analyze_video.py video.mp4 --transcribe --output result.json
```

脚本会自动从 `config.js` 读取 API Keys。

## 使用场景

### 场景1：拆解视频用于改写（走 script-rewriter 流程）
- 输出：`structure` + `reusable_template`
- 模板中台词用 `[]` 标注可替换部分
- 供 script-rewriter 改写使用

### 场景2：拆解视频直接复刻（跳过 script-rewriter）
- 输出：`structure` + `scenes` + `transcription`
- `scenes` 字段包含完整台词，可直接用于 ai-video-generator
- 保留原视频的台词和表达方式
- **关键**：必须使用 `--transcribe` 参数提取台词

## 脚本用法

```bash
python scripts/analyze_video.py <video_path> [--fps 5] [--transcribe] [--output output.json]

参数:
  video_path       视频文件路径
  --fps            抽帧频率 (0.2-5)，默认5
  --transcribe, -t 启用音频转录提取对白
  --output, -o     输出JSON文件路径
```

## fps调整

| 场景 | fps | 说明 |
|------|-----|------|
| 动作剧烈 | 2-5 | 运动类视频 |
| 画面平缓 | 0.5-1 | 口播、知识分享 |
| 节省token | 0.2-0.5 | 静态画面 |

## 输出格式

脚本输出JSON包含：

```json
{
  "duration": 60,
  "width": 1280,
  "height": 720,
  "ratio": "16:9",
  "type": "知识分享",
  "topic": "视频主题",
  "structure": [
    {"section": "黄金3秒", "time_range": "0-3秒", "scene": "...", "dialogue": "...", "shot_type": "特写", "purpose": "..."},
    {"section": "冲突设置", ...},
    {"section": "内容展开", "scenes": [...]},
    {"section": "反转高潮", ...},
    {"section": "CTA引导", ...}
  ],
  "reusable_template": {
    "hook": "台词模板，用[]标注可替换部分",
    "conflict": "...",
    "content_points": ["...", "...", "..."],
    "climax": "...",
    "cta": "..."
  },
  "scenes": [
    {"prompt": "人物描述+说：\"台词内容\"+表情+景别", "duration": 4},
    {"prompt": "人物描述+说：\"台词内容\"+表情+景别", "duration": 5},
    {"prompt": "人物描述+说：\"台词内容\"+手势+景别", "duration": 8},
    ...
  ],
  "resolution": "720p",
  "generate_audio": true,
  "transcription": {
    "text": "完整的音频转录文本",
    "utterances": [
      {
        "text": "分句文本",
        "start_time": 0,
        "end_time": 1705,
        "words": [...]
      }
    ]
  }
}
```

**注意**：
- `width`, `height`, `ratio` 字段由 ffprobe 自动检测
- `transcription` 字段仅在使用 `--transcribe` 参数时包含
- **`scenes` 字段**是为了直接对接 ai-video-generator 而设计的：
  - 将 `structure` 中的 `scene`、`dialogue`、`shot_type` 整合为 `prompt`
  - 台词用双引号包裹，格式：`人物描述+说："台词内容"+表情+景别`
  - `duration` 从 `time_range` 计算得出
  - 可直接用于 ai-video-generator，无需改写

## 生成 scenes 字段（对接 ai-video-generator）

为了让拆解结果可以直接用于 ai-video-generator 复刻视频，需要将 `structure` 转换为 `scenes` 格式：

### 转换规则

1. **提取每个片段的信息**：
   - `scene`：画面描述
   - `dialogue`：台词内容
   - `shot_type`：景别（特写/中景/全景）
   - `time_range`：时间范围（计算 duration）

2. **构建 prompt**：
   ```
   格式：人物描述 + 说："台词内容" + 表情/动作 + 景别
   示例：职场女性对着镜头说："这3个技巧，90%的人都不知道"，表情认真，特写镜头
   ```

3. **台词处理**：
   - 使用双引号包裹完整台词：`说："台词内容"`
   - 如果 `dialogue` 为空或无台词场景，省略台词部分
   - 保持台词的原始表达，不要改写

4. **duration 计算**：
   - 从 `time_range` 提取时长（如 "0-3秒" → 3秒）
   - 或使用 `transcription` 中的时间戳精确计算

### 示例

**structure → scenes 转换**：

```
structure:
{"section": "黄金3秒", "scene": "职场女性对着镜头", "dialogue": "这3个技巧，90%的人都不知道", "shot_type": "特写"}

↓

scenes:
{"prompt": "职场女性对着镜头说："这3个技巧，90%的人都不知道"，特写镜头", "duration": 3}
```

### 完整输出示例

```json
{
  "duration": 60,
  "width": 1080,
  "height": 1920,
  "ratio": "9:16",
  "type": "知识分享",
  "topic": "时间管理技巧",
  "structure": [...],
  "reusable_template": {...},
  "scenes": [
    {"prompt": "职场女性对着镜头说："这3个技巧，90%的人都不知道"，表情认真，特写镜头", "duration": 3},
    {"prompt": "职场女性继续说："你每天都在加班？其实效率比时间更重要"，中景", "duration": 5},
    {"prompt": "职场女性讲解第一个技巧说："第一，学会时间分块管理"，手势自然，中景", "duration": 12},
    {"prompt": "职场女性讲解第二个技巧说："第二，优先处理重要不紧急的事"，中景", "duration": 15},
    {"prompt": "职场女性讲解第三个技巧说："第三，每天留出30分钟深度思考"，中景", "duration": 15},
    {"prompt": "职场女性说："其实最重要的不是管理时间，而是管理精力"，表情严肃，特写镜头", "duration": 5},
    {"prompt": "职场女性微笑说："关注我，每天分享一个职场技巧"，挥手，中景", "duration": 5}
  ],
  "resolution": "720p",
  "generate_audio": true,
  "transcription": {
    "text": "这3个技巧，90%的人都不知道...",
    "utterances": [...]
  }
}
```

**使用方式**：
```bash
# 拆解视频（含台词）
python scripts/analyze_video.py video.mp4 --transcribe --output result.json

# 直接用于 ai-video-generator（无需改写）
python scripts/generate_all.py --script result.json --output-dir ./clips
```

## 黄金结构

| 部分 | 时间 | 目的 | 识别特征 |
|------|------|------|----------|
| 黄金3秒 | 0-3秒 | 吸引注意力 | 数字、悬念词、痛点 |
| 冲突设置 | 3-8秒 | 制造悬念 | 反问句、对比、困境 |
| 内容展开 | 8-50秒 | 提供价值 | 要点列举、案例 |
| 反转高潮 | 50-55秒 | 超出预期 | 转折词、深层洞察 |
| CTA引导 | 55-60秒 | 行动号召 | 关注、点赞、评论 |

## 音频转录功能

使用火山引擎语音识别极速版 API（豆包录音文件识别模型）提取视频对白。

### 功能特性

- **极速识别**：一次请求即返回结果，无需轮询等待
- **Base64上传**：支持直接上传音频文件，无需公网URL
- **文本规范化（ITN）**：自动将口语转换为书面形式（如"一九七零年" → "1970年"）
- **智能标点**：自动添加标点符号
- **语义顺滑**：删除停顿词、语气词、重复词
- **时间戳**：提供分句级和词级时间戳
- **支持多语言**：中英文、上海话、闽南语、粤语、四川话、陕西话等

### 使用限制

- 音频时长：≤2小时
- 音频大小：≤100MB
- 音频格式：WAV / MP3 / OGG OPUS

### 使用方法

```bash
# 单独使用音频转录（极速版）
python scripts/transcribe_audio.py video.mp4 --output transcription.json

# 与视频分析一起使用
python scripts/analyze_video.py video.mp4 --transcribe --output result.json
```

### 配置要求

需要在 `config.js` 中配置语音识别 API 凭证：

```javascript
SPEECH_APP_KEY: 'your_speech_app_key',
SPEECH_ACCESS_KEY: 'your_speech_access_key'
```

获取方式：https://console.volcengine.com/speech/service/8

**注意**：需要在控制台开通 `volc.bigasr.auc_turbo` 极速版权限

### 转录结果格式

```json
{
  "audio_info": {
    "duration": 26496
  },
  "result": {
    "text": "完整的音频转录文本",
    "utterances": [
      {
        "text": "分句文本",
        "start_time": 0,
        "end_time": 1705,
        "words": [
          {"text": "单词", "start_time": 740, "end_time": 860}
        ]
      }
    ]
  }
}
```

### 工作流程

1. **提取音频**：使用 ffmpeg 从视频提取音频（MP3格式，16kHz，单声道）
2. **Base64编码**：将音频文件转换为base64编码
3. **提交转录**：调用极速版API，一次请求即返回结果
4. **输出结果**：保存包含时间戳的转录文本

### 注意事项

- 音频转录需要额外的 API 凭证（SPEECH_APP_KEY 和 SPEECH_ACCESS_KEY）
- 极速版API响应速度快，通常几秒内返回结果
- 如果视频没有音频或音频为静音，转录会失败
- doubao-seed-1-8-251228 视频理解模型**不支持**音频识别，需要单独调用语音识别 API
