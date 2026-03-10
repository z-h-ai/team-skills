"""演示版本 - 用预设内容快速生成"""
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
OUTPUT_DIR = SKILL_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# 预设卡片
demo_cards = [
    {
        "question": "公司拖欠工资怎么办？",
        "answer": "用人单位未及时足额支付劳动报酬的，劳动者可以解除劳动合同并要求经济补偿。",
        "law_refs": "《劳动合同法》第38条",
        "comment": "工资是底线，拖欠就是违法。"
    },
    {
        "question": "加班费怎么算？",
        "answer": "工作日加班150%，休息日200%，法定节假日300%工资报酬。",
        "law_refs": "《劳动法》第44条",
        "comment": "加班不是义务，补偿是权利。"
    },
    {
        "question": "离职补偿怎么算？",
        "answer": "按工作年限，每满一年支付一个月工资。不满一年按一年算，不满半年付半个月。",
        "law_refs": "《劳动合同法》第47条",
        "comment": "离职有补偿，年限是关键。"
    }
]

# 加载模板
sys.path.insert(0, str(SKILL_DIR))
from templates import get_template

# 读取配置
def parse_persona(path):
    config = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            config[k.strip()] = v.strip()
    return config

cfg = parse_persona(SKILL_DIR / "inputs" / "persona.md")
LAWYER_NAME = cfg.get("lawyer_name", "律师")
LICENSE_NUMBER = cfg.get("license_number", "")

template = get_template("three_body")
print(f"🎨 使用模板: three_body (本地合成)")

# 生成
print("🖼️  生成海报...")
for i, card in enumerate(demo_cards, 1):
    output_path = OUTPUT_DIR / f"poster_{i:02d}.png"
    config = {
        "lawyer_name": LAWYER_NAME,
        "license_number": LICENSE_NUMBER,
        "portrait_part": None
    }
    success = template.generate_poster(card, config, output_path)
    if success:
        print(f"  ✅ {output_path.name}")
    else:
        print(f"  ❌ {output_path.name} 失败")

print(f"\n✨ 完成！生成了 3 张海报到 {OUTPUT_DIR}")
