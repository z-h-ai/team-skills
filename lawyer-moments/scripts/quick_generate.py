"""快速生成版本 - 跳过爬取，直接用内置法条"""
import os
import sys
from pathlib import Path
from google import genai
from google.genai import types
import random

# 路径
SKILL_DIR = Path(__file__).parent.parent
PERSONA_PATH = SKILL_DIR / "inputs" / "persona.md"
OUTPUT_DIR = SKILL_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# 读取配置
def parse_persona(path):
    config = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            config[k.strip()] = v.strip()
    return config

cfg = parse_persona(PERSONA_PATH)
LAWYER_NAME = cfg.get("lawyer_name", "律师")
LICENSE_NUMBER = cfg.get("license_number", "")
TEMPLATE_NAME = cfg.get("template", "three_body")
GEMINI_API_KEY = cfg.get("gemini_api_key", "")

# 内置法条
FALLBACK_ARTICLES = [
    "《劳动合同法》第47条：经济补偿按劳动者在本单位工作的年限，每满一年支付一个月工资的标准向劳动者支付。六个月以上不满一年的，按一年计算；不满六个月的，向劳动者支付半个月工资的经济补偿。",
    "《劳动法》第44条：安排劳动者延长工作时间的，支付不低于工资百分之一百五十的工资报酬；休息日安排劳动者工作又不能安排补休的，支付不低于工资百分之二百；法定休假日安排劳动者工作的，支付不低于工资百分之三百的工资报酬。",
    "《劳动合同法》第38条：用人单位未及时足额支付劳动报酬的，或未依法为劳动者缴纳社会保险费的，劳动者可以解除劳动合同并要求经济补偿。",
]

print("📋 使用内置法条...")
articles = random.sample(FALLBACK_ARTICLES, 3)

# 初始化 Gemini
print("🔧 初始化 Gemini...")
client = genai.Client(api_key=GEMINI_API_KEY)

# 生成金句
print("✍️  生成法律金句...")
cards = []
for i, article in enumerate(articles, 1):
    prompt = f"""你是{LAWYER_NAME}，请根据以下法条生成一个法律问答卡片：

法条：{article}

请生成：
1. 一个普通人会问的问题（15字内）
2. 简短答案（30字内）
3. 律师点评金句（20字内，要有个人风格）

格式：
问题：xxx
答案：xxx
金句：xxx"""
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    cards.append({
        "article": article,
        "content": response.text
    })
    print(f"  ✅ 卡片 {i}/3")

# 加载模板
sys.path.insert(0, str(SKILL_DIR))
from templates import get_template

template = get_template(TEMPLATE_NAME)
print(f"🎨 使用模板: {TEMPLATE_NAME}")

# 生成图片
print("🖼️  生成海报...")
for i, card in enumerate(cards, 1):
    output_path = OUTPUT_DIR / f"poster_{i:02d}.png"
    
    # 解析卡片内容
    lines = card["content"].strip().split("\n")
    case_data = {"law_refs": card["article"]}
    for line in lines:
        if line.startswith("问题："):
            case_data["question"] = line.replace("问题：", "").strip()
        elif line.startswith("答案："):
            case_data["answer"] = line.replace("答案：", "").strip()
        elif line.startswith("金句："):
            case_data["comment"] = line.replace("金句：", "").strip()
    
    config = {
        "gemini_client": client,
        "lawyer_name": LAWYER_NAME,
        "license_number": LICENSE_NUMBER,
        "portrait_part": None
    }
    
    success = template.generate_poster(case_data, config, output_path)
    if success:
        print(f"  ✅ {output_path.name}")
    else:
        print(f"  ❌ {output_path.name} 生成失败")

print(f"\n✨ 完成！生成了 3 张海报到 {OUTPUT_DIR}")
