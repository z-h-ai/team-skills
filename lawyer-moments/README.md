# 律师每日朋友圈配图生成器 — 安装指南

一键生成专业法律朋友圈海报：法条 + 个性点评金句 + 你的真人形象。

## 安装步骤（3 分钟搞定）

### 1. 把整个文件夹放到 Cursor Skills 目录

```bash
cp -r lawyer-moments-skill ~/.cursor/skills/lawyer-moments
```

### 2. 安装 Python 依赖

```bash
pip install rembg pillow playwright google-genai
playwright install chromium
```

### 3. 获取 Gemini API Key

前往 https://aistudio.google.com/apikey 创建免费 API Key。

### 4. 在 Cursor 中触发

打开 Cursor，新建对话，输入：

```
/lawyer-moments
```

跟着对话提示填写你的信息（名字、照片、风格、API Key），完成后自动生成 3 张海报！

## 目录结构

```
lawyer-moments/
├── SKILL.md              # Skill 定义（Cursor 读取）
├── README.md             # 本文件
├── inputs/
│   ├── persona.md        # 你的配置（首次运行时自动填写）
│   └── portrait_cutout.png  # 你的抠图照片（首次运行时生成）
├── scripts/
│   ├── generate_posters.py  # 主脚本
│   └── fetch_law.py         # 法条获取
└── output/               # 生成的海报图片
```

## 效果示例

深蓝金色专业法律海报，包含：
- 标题「每日一法」
- 法条原文
- 你的个性化点评金句
- 你的真人半身照
- 签名和执照号

每次运行随机选取不同法条，每天发不重样！
