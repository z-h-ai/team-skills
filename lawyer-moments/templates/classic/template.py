"""
经典模板：深蓝金色专业法律海报
使用 Gemini 图片生成模型，支持真人参考图
"""
import base64
from google.genai import types

TEMPLATE_INFO = {
    "name": "classic",
    "display_name": "经典深蓝金",
    "description": "深蓝金色专业法律海报，Gemini AI 生图，包含法槌、天平等法律元素",
}

IMAGE_MODELS = [
    "gemini-3-pro-image-preview",
    "gemini-3.1-flash-image-preview",
    "gemini-2.5-flash-image",
]


def _build_prompt(case, lawyer_name, license_number, has_portrait):
    signature = f"律师执照号：{license_number}" if license_number else ""
    portrait_instruction = (
        "Bottom right: glowing gold square frame. "
        "Place the provided reference portrait photo of the lawyer inside this gold frame, "
        "maintaining the person's real appearance, clothing, and facial features exactly as shown in the reference photo."
    ) if has_portrait else (
        "Bottom right: glowing gold square frame containing a professional Asian lawyer portrait, "
        "half-body, in business attire, smiling confidently."
    )
    law_text = case.get('law') or case.get('answer', '')
    quote_text = case.get('quote') or case.get('comment', '')
    return (
        f"Generate a professional legal WeChat Moments poster image.\n\n"
        f"VISUAL STYLE:\n"
        f"- Background: Deep navy blue gradient (#0a1628) with subtle star particle texture\n"
        f"- Border: Elegant gold double-line border with ornate Victorian corner decorations\n"
        f"- Color palette: Navy Blue, Gold (#c9a84c), White\n"
        f"- Atmosphere: Trustworthy, authoritative, sophisticated\n"
        f"- Aspect ratio: 3:4 portrait orientation for smartphone WeChat Moments\n\n"
        f"LAYOUT (top to bottom):\n"
        f"1. Header: '每日一法' in bold gold 3D serif font, centered at top\n"
        f"2. Decorative gold horizontal divider line\n"
        f"3. Main content block (semi-transparent dark rounded rectangle, center):\n"
        f"   - TOP: Law article in white text:\n"
        f"     '{law_text}'\n"
        f"   - MIDDLE: Decorative gold separator line\n"
        f"   - BOTTOM:\n"
        f"     '{lawyer_name}点评：' in gold bold font\n"
        f"     '{quote_text}' in white font\n"
        f"4. Bottom area:\n"
        f"   - LEFT: Signature '{signature}' in gold bold serif\n"
        f"   - {portrait_instruction}\n"
        f"5. Decorative props: 3D wooden gavel bottom-left, golden scales of justice mid-right\n\n"
        f"Typography: Gold serif for headings, white sans-serif for body. High contrast and legibility."
    )


def generate_poster(case, config, output_path) -> bool:
    """使用 Gemini 图片模型生成经典风格海报"""
    client = config["gemini_client"]
    portrait_part = config.get("portrait_part")
    lawyer_name = config["lawyer_name"]
    license_number = config.get("license_number", "")
    preferred_model = config.get("preferred_model")

    prompt = _build_prompt(case, lawyer_name, license_number, portrait_part is not None)

    contents = [prompt]
    if portrait_part:
        contents.append(portrait_part)

    models = [preferred_model] + IMAGE_MODELS if preferred_model else IMAGE_MODELS
    models = list(dict.fromkeys(models))

    for model in models:
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
                print(f"  {model}: 失败 - {err[:100]}")
    return False
