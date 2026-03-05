---
name: lawyer-moments
description: 律师每日朋友圈配图自动生成器。通过四步对话收集律师称呼、执照号、头像照片、个人风格，自动生成包含法条+金句+律师真人形象的朋友圈配图。触发词：律师朋友圈、每日配图、法条金句、朋友圈生成器、lawyer moments。
---

# 律师每日朋友圈配图生成器

## 目录结构

```
~/.cursor/skills/lawyer-moments/
├── SKILL.md                        # 本文件
├── inputs/
│   ├── persona.md                  # 用户配置（Setup 后自动生成）
│   ├── portrait_cutout.png         # 抠图后的真人照片
│   └── personas/                   # persona 文件库
│       └── liulv.md                # 刘律师 persona
├── templates/                      # 模板系统
│   ├── __init__.py                 # 模板注册表（自动发现所有模板）
│   ├── classic/                    # 经典深蓝金色模板（Gemini 生图）
│   │   └── template.py
│   ├── minimal_biz/                # 商务蓝模板（Gemini 生图）
│   │   └── template.py
│   └── three_body/                 # 三体宇宙模板（Pillow 合成）
│       ├── template.py
│       └── backgrounds/            # 9 张三体风格背景图
├── scripts/
│   ├── generate_posters.py         # 主脚本：法条获取 + 金句生成 + 模板调用
│   └── fetch_law.py               # 法条获取（Playwright 爬取 + 内置备用）
└── output/                         # 生成的图片（自动创建）
```

## 可用模板

| 模板名 | 显示名 | 生图方式 | 说明 |
|--------|--------|---------|------|
| `classic` | 经典深蓝金 | Gemini AI 生图 | 深蓝金色法律海报，含法槌、天平等元素，权威感 |
| `minimal_biz` | 商务蓝 | Gemini AI 生图 | 企业蓝 + 风景摄影背景 + 几何色块排版，高端商务感 |
| `three_body` | 三体宇宙 | Pillow 本地合成 | 三体科幻背景图 + 文字合成，冰蓝色调，速度快 |

## 工作流程

收到用户触发后，按以下顺序执行：

### Step 0：检查 Setup

检查 `inputs/persona.md` 是否已有值。若未完成，先引导完成 Setup（见下方）。若已完成，进入 Step 1。

### Step 1：每次运行都让用户选择模板（必须）

**每次触发生成时，都必须先让用户选择模板**，不要直接使用 persona.md 中的默认值。

使用 AskQuestion 工具展示所有可用模板，让用户选择：

> 请选择本次海报模板风格：
> 1. **经典深蓝金** — 深蓝金色法律海报，Gemini AI 生图，法槌天平元素，权威感
> 2. **商务蓝** — 企业蓝 + 风景摄影背景 + 几何色块排版，Gemini AI 生图，高端商务感
> 3. **三体宇宙** — 三体科幻背景 + Pillow 文字合成，冰蓝色调，速度快

用户选择后，将选中的模板名写入 `inputs/persona.md` 的 `template:` 字段，然后进入 Step 2。

### Step 2：搜索法条 + 生成金句

运行 `scripts/generate_posters.py`，脚本会自动：
1. 获取法条（Playwright 爬取，失败降级内置备用）
2. 用 Gemini 文本模型生成法律问答 + 金句
3. 用选定的模板生成 3 张图片到 `output/`

### Step 3：展示结果

读取 `output/poster_01.png`、`poster_02.png`、`poster_03.png` 展示给用户。

---

## Setup：收集律师信息（仅首次运行）

### 系统 Setup

```bash
pip install rembg pillow playwright google-genai
playwright install chromium
```

### 用户 Setup

依次引导用户填写以下字段，完成后保存到 `inputs/persona.md`：

---

**字段 1：lawyer_name（必填）**

> 你好！我来帮你设置每日朋友圈配图自动推送。
> **第一步：请告诉我你的称呼**，例如"刘律师"、"张律师"。

---

**字段 2：license_number（选填）**

> **第二步（选填）**：请提供你的律师执业证编号，会显示在图片底部增加专业感。没有也可以跳过。

---

**字段 3：portrait_image（必填）**

> **第三步**：请发送一张你的职业装半身照片（正面照最佳）。

收到图片后，若背景不透明，自动调用 rembg 抠图：

```python
from rembg import remove
with open(input_path, 'rb') as f:
    output_data = remove(f.read())
with open('inputs/portrait_cutout.png', 'wb') as f:
    f.write(output_data)
```

---

**字段 4：你的个性（两种方式，二选一）**

**方式 A：使用预制 persona 文件（推荐）**

> **第四步**：我们已经有一份预制的刘律师详细 persona 文件（`inputs/personas/liulv.md`），包含专业定位、语言风格、金句示例和 System Prompt。
> 如果直接使用，在 `persona.md` 中设置：
> ```
> persona_file: personas/liulv.md
> ```

用户也可以参考此文件格式，创建自己的 persona 文件放在 `inputs/personas/` 目录下。

**方式 B：直接输入简短风格描述**

> **第四步**：请把下面这段话复制，发给你平时常用的 AI（豆包、ChatGPT 都行），然后把 AI 的回复粘贴回来给我：
>
> 「请根据我们的历史对话，总结一下我的语言表达风格，包括：常用句式、语气特点（严肃/幽默/毒蛇/温暖）、喜欢用什么方式打比方。请用 3-5 句具体的话描述，不要太笼统，最后给出一句"如果让你模仿我的风格写一句话，会是什么样的"示例。」

若无历史，可直接描述风格或从预设选择：毒蛇犀利 / 温和专业 / 接地气幽默。
在 `persona.md` 中设置：
```
persona: 接地气幽默
```

---

**Setup 完成后**，保存到 `inputs/persona.md`：

```markdown
lawyer_name: 苏律师
license_number:
portrait_cutout: inputs/portrait_cutout.png
persona_file: personas/liulv.md   # 使用预制persona文件（优先）
# persona: 接地气幽默             # 或直接写简短风格描述（二选一）
template: classic
gemini_api_key: YOUR_GEMINI_API_KEY
```

---

## 法条获取

优先通过 Playwright 爬取 `flk.npc.gov.cn`（全国人大法律法规数据库），失败自动降级使用内置 10 条劳动法相关法条随机抽取。

每次运行随机从以下关键词中选 1 个搜索：
`["劳动合同", "工资报酬", "解除劳动合同", "经济补偿", "工作时间", "休息休假", "社会保险", "劳动保护", "违约金", "竞业限制"]`

## 金句生成

使用 `gemini-2.5-flash` 文本模型，根据法条 + 用户 persona 风格，为每条法条生成完整法律问答卡片（问题 + 答案 + 法条依据 + 律师点评金句）。

---

## 运行方式

```bash
cd ~/.cursor/skills/lawyer-moments/scripts
python generate_posters.py
```

生成 3 张图片到 `output/` 目录。

---

## 常见问题处理

- **用户说没有豆包历史**：让用户直接描述风格，或选择预设风格
- **用户没有照片**：使用 AI 生成虚拟人像
- **照片背景不透明**：自动调用 rembg 抠图
- **Gemini API Key 未设置**：提示在 `inputs/persona.md` 中填写 `gemini_api_key`
- **flk.npc.gov.cn 爬取失败**：自动降级为内置法条，不影响整体流程
- **图片生成模型 503 繁忙**：自动降级到下一个备选模型（仅 Gemini 生图模板）
