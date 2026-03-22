# Team Skills

团队共享的 AI Skills，可安装到 Cursor / Claude Code 使用。

## 已有 Skills

| Skill | 说明 | 触发词 |
|-------|------|--------|
| [business-contract-generator](./business-contract-generator/) | 中国法下商业合同生成（服务/采购/合作等） | 合同、协议、服务协议 |
| [markdown-to-docx](./markdown-to-docx/) | Markdown 转 Word（.docx），保留表格与代码块等 | `markdown to docx`、转 Word |
| [markdown-to-pdf](./markdown-to-pdf/) | Markdown 转 PDF，可自定义版式 | `markdown to pdf`、转 PDF |
| [video-analyzer](./video-analyzer/) | 短视频拆解：结构、台词、节奏 → 可复用脚本模板 | `拆解视频`、`视频拆解`、`提取脚本模板` |
| [script-rewriter](./script-rewriter/) | 基于爆款模板改写新主题脚本（对接 ai-video-generator） | `改写脚本`、`换个主题`、`脚本改写` |
| [ai-video-generator](./ai-video-generator/) | 脚本 JSON → Seedance 片段 + FFmpeg 拼接成片 | `生成视频`、`脚本转视频`、`制作短视频` |

**短视频流水线**：`video-analyzer` → `script-rewriter` → `ai-video-generator`。

## 安装方式

### Cursor

将 skill 文件夹复制到 `~/.cursor/skills/` 目录下即可：

```bash
cp -r video-analyzer ~/.cursor/skills/
cp -r script-rewriter ~/.cursor/skills/
cp -r ai-video-generator ~/.cursor/skills/
```

其他 skill 同理，将文件夹名替换为上表中的目录名。

### Claude Code

将 skill 文件夹复制到 `~/.claude/skills/` 目录下即可：

```bash
cp -r video-analyzer ~/.claude/skills/
cp -r script-rewriter ~/.claude/skills/
cp -r ai-video-generator ~/.claude/skills/
```

### 配置说明

- **video-analyzer / ai-video-generator**：需在项目根目录配置 `config.js`（如 `ARK_API_KEY`；转录另需火山语音相关 Key，见各 skill 内 `SKILL.md`）。
- **business-contract-generator** 等文档类 skill：按各自 `SKILL.md` 安装依赖（如 pandoc）。
