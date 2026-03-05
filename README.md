# Team Skills

团队共享的 AI Skills，可安装到 Cursor / Claude Code 使用。

## 已有 Skills

| Skill | 说明 | 触发词 |
|-------|------|--------|
| [lawyer-moments](./lawyer-moments/) | 律师每日朋友圈配图生成器（法条 + 金句 + 真人形象） | `律师朋友圈`、`每日配图`、`lawyer moments` |

## 安装方式

### Cursor

将 skill 文件夹复制到 `~/.cursor/skills/` 目录下即可：

```bash
cp -r lawyer-moments ~/.cursor/skills/
```

### Claude Code

将 skill 文件夹复制到 `~/.claude/skills/` 目录下即可：

```bash
cp -r lawyer-moments ~/.claude/skills/
```

安装后首次运行会引导你完成 Setup（填写称呼、照片、风格等）。
