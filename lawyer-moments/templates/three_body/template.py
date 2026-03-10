"""
三体模板：使用预制三体宇宙背景图 + Pillow 合成文字和头像
布局：问题 → 答案（带法条分析）→ 法条依据 → 律师点评
"""
import re
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

TEMPLATE_INFO = {
    "name": "three_body",
    "display_name": "三体宇宙",
    "description": "三体科幻风格，预制宇宙背景图 + Pillow 文字合成，无需 Gemini 生图",
}

BACKGROUNDS_DIR = Path(__file__).parent / "backgrounds"

# 海报尺寸（3:4 竖版微信朋友圈）
POSTER_W, POSTER_H = 900, 1200

# 颜色
COLOR_WHITE = (255, 255, 255)
COLOR_CYAN = (0, 212, 255)
COLOR_GOLD = (201, 168, 76)
COLOR_LIGHT_GRAY = (200, 200, 210)

# 字体路径（Linux）
FONT_BOLD = "/usr/share/fonts/google-noto-cjk/NotoSansCJK-Bold.ttc"
FONT_REGULAR = "/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc"

_used_backgrounds = []


def _strip_markdown(text):
    """清除 Gemini 返回的 markdown 格式标记，Pillow 无法渲染"""
    if not text:
        return text
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # **加粗**
    text = re.sub(r'\*(.+?)\*', r'\1', text)       # *斜体*
    text = re.sub(r'__(.+?)__', r'\1', text)       # __加粗__
    text = re.sub(r'_(.+?)_', r'\1', text)         # _斜体_
    text = re.sub(r'~~(.+?)~~', r'\1', text)       # ~~删除线~~
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)  # # 标题
    text = re.sub(r'`(.+?)`', r'\1', text)         # `代码`
    return text


def _get_font(path, size, index=0):
    try:
        return ImageFont.truetype(path, size, index=index)
    except Exception:
        return ImageFont.load_default()


def _pick_background():
    global _used_backgrounds
    bgs = sorted(BACKGROUNDS_DIR.glob("*.png"))
    if not bgs:
        return None
    available = [b for b in bgs if b not in _used_backgrounds]
    if not available:
        _used_backgrounds.clear()
        available = bgs
    chosen = random.choice(available)
    _used_backgrounds.append(chosen)
    return chosen


def _wrap_text(text, font, max_width, draw):
    lines = []
    for paragraph in text.split("\n"):
        current_line = ""
        for char in paragraph:
            test_line = current_line + char
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] > max_width:
                if current_line:
                    lines.append(current_line)
                current_line = char
            else:
                current_line = test_line
        if current_line:
            lines.append(current_line)
    return lines


def generate_poster(case, config, output_path) -> bool:
    """使用 Pillow 合成三体风格法律问答海报"""
    lawyer_name = config["lawyer_name"]
    license_number = config.get("license_number", "")
    portrait_path = config.get("portrait_path")
    if portrait_path:
        portrait_path = Path(portrait_path)

    # 兼容旧格式（law+quote）和新格式（question+answer+law_refs+comment）
    # 清除 Gemini 可能返回的 markdown 格式标记
    question = _strip_markdown(case.get("question", ""))
    answer = _strip_markdown(case.get("answer", case.get("law", "")))
    law_refs = _strip_markdown(case.get("law_refs", ""))
    comment = _strip_markdown(case.get("comment", case.get("quote", "")))

    # 1. 加载背景图
    bg_path = _pick_background()
    if bg_path is None:
        print("  错误：未找到三体背景图")
        return False

    print(f"  背景: {bg_path.name}")
    bg = Image.open(bg_path).convert("RGBA")
    bg = bg.resize((POSTER_W, POSTER_H), Image.LANCZOS)

    # 2. 创建合成层
    overlay = Image.new("RGBA", (POSTER_W, POSTER_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # 3. 加载字体（全部使用粗体，暗背景上细体看不清）
    font_title = _get_font(FONT_BOLD, 46)
    font_question = _get_font(FONT_BOLD, 30)
    font_answer = _get_font(FONT_BOLD, 24)
    font_law_refs = _get_font(FONT_BOLD, 22)
    font_comment_label = _get_font(FONT_BOLD, 26)
    font_comment = _get_font(FONT_BOLD, 24)
    font_sig = _get_font(FONT_BOLD, 22)

    # 4. 布局参数
    margin_x = 50
    text_pad = 16
    content_w = POSTER_W - margin_x * 2
    text_w = content_w - text_pad * 2

    has_portrait = portrait_path and portrait_path.exists()
    portrait_reserve_w = 190 if has_portrait else 0

    # 5. 计算各区域文字
    # 行高
    title_h = 56
    question_lh = 46
    answer_lh = 40
    law_refs_lh = 36
    comment_lh = 40
    sig_h = 32
    sep_h = 28
    padding = 28

    max_content_h = POSTER_H - int(POSTER_H * 0.12) - 40

    question_text = f"问：{question}" if question else ""
    question_lines = _wrap_text(question_text, font_question, text_w, draw) if question_text else []

    # 预截断答案（最多 280 字，防止内容过长）
    answer_trimmed = answer if len(answer) <= 280 else answer[:277] + "……"
    answer_text = f"答：{answer_trimmed}" if answer_trimmed else answer_trimmed
    answer_lines = _wrap_text(answer_text, font_answer, text_w, draw)

    law_refs_text = f"法条依据：{law_refs}" if law_refs else ""
    law_refs_lines = _wrap_text(law_refs_text, font_law_refs, text_w, draw) if law_refs_text else []

    comment_label = f"{lawyer_name}点评："
    comment_w = text_w - portrait_reserve_w
    comment_lines = _wrap_text(comment, font_comment, comment_w, draw)

    def _calc_content_h():
        return (
            padding +
            title_h + 16 +
            sep_h + 12 +
            len(question_lines) * question_lh + 16 +
            len(answer_lines) * answer_lh + 16 +
            (len(law_refs_lines) * law_refs_lh + 12 if law_refs_lines else 0) +
            sep_h + 12 +
            comment_lh +
            len(comment_lines) * comment_lh + 16 +
            sig_h +
            padding
        )

    content_h = _calc_content_h()

    # 如果仍然超高，逐行裁剪答案直到不超
    while content_h > max_content_h and len(answer_lines) > 3:
        answer_lines = answer_lines[:-1]
        answer_lines[-1] = answer_lines[-1].rstrip() + "……"
        content_h = _calc_content_h()

    # 内容区域起始位置（允许从更高位置开始，保证内容不溢出底部）
    content_top = max(POSTER_H - content_h - 50, int(POSTER_H * 0.15))

    # 6. 绘制半透明蒙版
    mask = Image.new("RGBA", (POSTER_W, POSTER_H), (0, 0, 0, 0))
    mask_draw = ImageDraw.Draw(mask)

    # 渐变过渡（加深蒙版，确保文字清晰可读）
    grad_h = 120
    for gy in range(content_top - grad_h, content_top):
        alpha = int(220 * (gy - (content_top - grad_h)) / grad_h)
        mask_draw.line([(0, gy), (POSTER_W, gy)], fill=(0, 0, 10, alpha))

    mask_draw.rectangle([0, content_top, POSTER_W, POSTER_H], fill=(0, 0, 10, 220))
    overlay = Image.alpha_composite(overlay, mask)
    draw = ImageDraw.Draw(overlay)

    # 7. 绘制内容
    y = content_top + padding

    # 标题
    title_text = "每 日 一 法"
    tb = draw.textbbox((0, 0), title_text, font=font_title)
    draw.text(((POSTER_W - (tb[2] - tb[0])) / 2, y), title_text, fill=COLOR_CYAN, font=font_title)
    y += title_h + 16

    # 分隔线 + 菱形
    lx1, lx2 = margin_x + 30, POSTER_W - margin_x - 30
    cy = y + sep_h // 2
    draw.line([(lx1, cy), (lx2, cy)], fill=(*COLOR_CYAN, 140), width=1)
    cx = POSTER_W // 2
    d = 5
    draw.polygon([(cx, cy - d), (cx + d, cy), (cx, cy + d), (cx - d, cy)], fill=COLOR_CYAN)
    y += sep_h + 12

    # 问题
    for line in question_lines:
        draw.text((margin_x + text_pad, y), line, fill=COLOR_CYAN, font=font_question)
        y += question_lh
    y += 16

    # 答案
    for line in answer_lines:
        draw.text((margin_x + text_pad, y), line, fill=COLOR_WHITE, font=font_answer)
        y += answer_lh
    y += 16

    # 法条依据
    if law_refs_lines:
        for line in law_refs_lines:
            draw.text((margin_x + text_pad, y), line, fill=COLOR_LIGHT_GRAY, font=font_law_refs)
            y += law_refs_lh
        y += 12

    # 第二条分隔线
    cy2 = y + sep_h // 2
    draw.line([(lx1, cy2), (lx2, cy2)], fill=(*COLOR_CYAN, 100), width=1)
    y += sep_h + 12

    # 律师点评标签
    draw.text((margin_x + text_pad, y), comment_label, fill=COLOR_CYAN, font=font_comment_label)
    y += comment_lh

    # 点评内容
    for line in comment_lines:
        draw.text((margin_x + text_pad, y), line, fill=COLOR_GOLD, font=font_comment)
        y += comment_lh
    y += 16

    # 签名（仅在有执照号时显示）
    if license_number:
        sig_text = f"执照号：{license_number}"
        draw.text((margin_x + text_pad, y), sig_text, fill=(*COLOR_GOLD, 180), font=font_sig)

    # 8. 合成
    result = Image.alpha_composite(bg, overlay)

    # 9. 头像
    if has_portrait:
        try:
            portrait = Image.open(portrait_path).convert("RGBA")
            ph = 170
            pw = int(portrait.width * ph / portrait.height)
            portrait = portrait.resize((pw, ph), Image.LANCZOS)

            px = POSTER_W - pw - 36
            py = POSTER_H - ph - 36

            border = 2
            border_img = Image.new("RGBA", (pw + border * 2, ph + border * 2), (0, 0, 0, 0))
            bd = ImageDraw.Draw(border_img)
            bd.rectangle([0, 0, pw + border * 2 - 1, ph + border * 2 - 1],
                         outline=(*COLOR_CYAN, 160), width=border)
            result.paste(border_img, (px - border, py - border), border_img)
            result.paste(portrait, (px, py), portrait)
        except Exception as e:
            print(f"  头像叠加失败: {e}")

    # 10. 保存
    result = result.convert("RGB")
    result.save(str(output_path), "PNG", quality=95)
    print(f"  已保存：{output_path}（Pillow 合成）")
    return True
