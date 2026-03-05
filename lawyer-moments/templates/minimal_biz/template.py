"""
商务蓝模板：企业蓝 + 风景摄影 + 几何色块分区
使用 Gemini 图片生成模型，参考高端商务 PPT 视觉风格
设计理念：蓝色系主色调、雪山/城市天际线等大气风景做背景、
         白色几何色块承载文字内容、律师头像嵌入金色圆框
"""
import base64
from google.genai import types

TEMPLATE_INFO = {
    "name": "minimal_biz",
    "display_name": "商务蓝",
    "description": "企业蓝商务风，风景摄影背景 + 几何色块排版，Gemini AI 生图",
}

IMAGE_MODELS = [
    "gemini-3-pro-image-preview",
    "gemini-3.1-flash-image-preview",
    "gemini-2.5-flash-image",
]


def _build_prompt(case, lawyer_name, license_number, has_portrait):
    signature = f"执照号 {license_number}" if license_number else ""

    question = case.get("question", "")
    answer = case.get("answer", case.get("law", ""))
    if len(answer) > 200:
        answer = answer[:197] + "……"
    law_refs = case.get("law_refs", "")
    comment = case.get("comment", case.get("quote", ""))

    portrait_instruction = (
        "Bottom-right corner: Place the provided reference photo of the lawyer inside a small "
        "circular frame with thin white border, positioned at the bottom-right of the comment card."
    ) if has_portrait else (
        "Bottom-right corner: A small circular placeholder icon representing a professional lawyer."
    )

    return (
        f"Generate a premium corporate-style legal knowledge card image for WeChat Moments.\n\n"
        f"VISUAL REFERENCE — Think of a high-end corporate PPT / keynote slide:\n"
        f"- Primary color: Corporate blue (#1a5fa0 to #2878c8 gradient)\n"
        f"- Background: UPPER 40% — a stunning landscape photo (snow-capped mountains, blue sky, or modern city skyline) "
        f"with a blue color overlay tint. The landscape creates a premium, aspirational atmosphere.\n"
        f"- Background: LOWER 60% — solid white or very light gray (#f5f5f7) clean area for text content.\n"
        f"- The transition between photo and white area uses a clean diagonal cut or subtle gradient blend.\n"
        f"- Aspect ratio: 3:4 portrait (900x1200px) for WeChat Moments.\n\n"
        f"LAYOUT (top to bottom):\n"
        f"1. TOP BANNER (on the landscape photo, upper-left):\n"
        f"   - A small blue geometric logo/icon (abstract scales of justice or diamond shape)\n"
        f"   - Text '每日一法' in bold white sans-serif font, large, with letter-spacing\n"
        f"   - Subtitle '{lawyer_name} · 法律顾问日签' in smaller white text below\n\n"
        f"2. MAIN CONTENT AREA (on white background, clean and spacious):\n"
        f"   - LEFT blue vertical accent bar (4px wide, corporate blue) along the left margin\n"
        f"   - Question in bold dark blue text (#1a3d6e), 1-2 lines:\n"
        f"     '问：{question}'\n"
        f"   - Thin light gray horizontal divider line\n"
        f"   - Answer in dark charcoal (#333333) regular weight text, well-spaced:\n"
        f"     '{answer}'\n"
        f"   - Law reference in small muted gray text:\n"
        f"     '法条依据：{law_refs}'\n\n"
        f"3. COMMENT CARD (bottom section, light blue-gray background card #edf2f8, rounded corners):\n"
        f"   - Left edge: thin gold/amber accent bar (#b28e48)\n"
        f"   - Label: '{lawyer_name}点评' in bold dark blue\n"
        f"   - Comment text in gold/amber color (#8a6d2b), bold:\n"
        f"     '{comment}'\n"
        f"   - {portrait_instruction}\n"
        f"   - Signature: '{signature}' in small muted text\n\n"
        f"4. BOTTOM: Thin corporate blue bar (4px) as footer accent\n\n"
        f"TYPOGRAPHY RULES:\n"
        f"- ALL text must be in Chinese (Simplified)\n"
        f"- Headings: Bold sans-serif (like PingFang SC Bold or Noto Sans CJK Bold)\n"
        f"- Body: Regular weight sans-serif, generous line-height\n"
        f"- HIGH legibility — text must be sharp and readable on mobile\n"
        f"- NO decorative/fantasy fonts, NO serif fonts\n\n"
        f"OVERALL MOOD: Professional, trustworthy, premium corporate feel. "
        f"Like a top-tier consulting firm's presentation slide. Clean, modern, confident."
    )


def generate_poster(case, config, output_path) -> bool:
    """使用 Gemini 图片模型生成商务蓝风格海报"""
    client = config["gemini_client"]
    portrait_part = config.get("portrait_part")
    lawyer_name = config["lawyer_name"]
    license_number = config.get("license_number", "")

    prompt = _build_prompt(case, lawyer_name, license_number, portrait_part is not None)

    contents = [prompt]
    if portrait_part:
        contents.append(portrait_part)

    for model in IMAGE_MODELS:
        try:
            print(f"  尝试模型: {model}...")
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"])
            )
            cand = response.candidates[0]
            if cand.content is None:
                print(f"  {model}: content=None, finish_reason={cand.finish_reason}")
                continue
            for part in cand.content.parts:
                d = getattr(part, "inline_data", None)
                if d and d.data:
                    img = d.data if isinstance(d.data, bytes) else base64.b64decode(d.data)
                    print(f"  {model}: 成功 ({len(img):,} bytes)")
                    output_path.write_bytes(img)
                    return True
            print(f"  {model}: 响应中未找到图片数据")
        except Exception as e:
            err = str(e)
            if "503" in err or "UNAVAILABLE" in err or "high demand" in err:
                print(f"  {model}: 服务繁忙，尝试下一个模型...")
            else:
                print(f"  {model}: 失败 - {err[:150]}")
    return False
