"""
律师每日朋友圈配图生成器
- 法条来源：Playwright 爬取 flk.npc.gov.cn，失败自动降级内置法条
- 金句生成：gemini-2.5-flash 文本模型
- 图片生成：通过模板系统（classic=Gemini生图，three_body=Pillow合成）
"""
import os
import sys
from pathlib import Path
from google import genai
from google.genai import types

sys.path.insert(0, str(Path(__file__).parent))
from fetch_law import get_law_articles

# ── 路径 ──────────────────────────────────────────────────
SKILL_DIR = Path(__file__).parent.parent
PERSONA_PATH = SKILL_DIR / "inputs" / "persona.md"
PORTRAIT_PATH = SKILL_DIR / "inputs" / "portrait_cutout.png"
OUTPUT_DIR = SKILL_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# 把 templates 目录加入 import 路径
sys.path.insert(0, str(SKILL_DIR))
from templates import get_template, list_templates

# ── 读取配置 ──────────────────────────────────────────────
def parse_persona(path):
    config = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            config[k.strip()] = v.strip()
    return config

cfg = parse_persona(PERSONA_PATH)
LAWYER_NAME    = cfg.get("lawyer_name", "律师")
LICENSE_NUMBER = cfg.get("license_number", "")
TEMPLATE_NAME  = cfg.get("template", "classic")
GEMINI_API_KEY = cfg.get("gemini_api_key", os.environ.get("GEMINI_API_KEY", ""))

# ── 加载 persona 风格 ────────────────────────────────────
# 优先级：persona_file（详细.md文件）> persona（简短描述）
PERSONA_FILE = cfg.get("persona_file", "")
PERSONA_CONTENT = None  # 详细 persona 文件的全文
PERSONA_SYSTEM_PROMPT = None  # 从详细文件中提取的 System Prompt

if PERSONA_FILE:
    persona_file_path = SKILL_DIR / "inputs" / PERSONA_FILE
    if persona_file_path.exists():
        PERSONA_CONTENT = persona_file_path.read_text(encoding="utf-8")
        print(f"已加载详细 persona 文件: {PERSONA_FILE}")
        # 提取 System Prompt（```代码块中的内容）
        import re
        code_blocks = re.findall(r'```\n(.*?)```', PERSONA_CONTENT, re.DOTALL)
        if code_blocks:
            PERSONA_SYSTEM_PROMPT = code_blocks[0].strip()
        # 提取 persona: 行
        persona_match = re.search(r'^persona:\s*(.+)$', PERSONA_CONTENT, re.MULTILINE)
        PERSONA = persona_match.group(1).strip() if persona_match else cfg.get("persona", "专业严谨")
    else:
        print(f"警告：persona_file '{PERSONA_FILE}' 不存在，使用简短 persona")
        PERSONA = cfg.get("persona", "专业严谨")
else:
    PERSONA = cfg.get("persona", "专业严谨")

if not GEMINI_API_KEY:
    print("错误：请在 inputs/persona.md 中填写 gemini_api_key")
    sys.exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)

# ── 加载模板 ──────────────────────────────────────────────
print(f"\n可用模板: {[t['display_name'] for t in list_templates()]}")
print(f"当前模板: {TEMPLATE_NAME}")

try:
    template = get_template(TEMPLATE_NAME)
except ValueError as e:
    print(f"错误：{e}")
    sys.exit(1)

print(f"已加载模板: {template.TEMPLATE_INFO['display_name']} — {template.TEMPLATE_INFO['description']}\n")

# ── Step 2: 获取法条 + 生成法律问答 ──────────────────────
import json as _json

PERSONA_STYLE_MAP = {
    "接地气幽默": "用接地气、幽默风趣的语言，像朋友聊天一样，把法律说得通俗易懂，带点调侃但不失专业",
    "毒蛇犀利":   "用犀利毒舌的风格，一针见血，让人印象深刻，有点辛辣但句句在理",
    "温和专业":   "用温和、专业、有权威感的语言，让人信任，像一位靠谱的顾问在耐心解释",
}
style_desc = PERSONA_STYLE_MAP.get(PERSONA, PERSONA)

QA_PROMPT_TEMPLATE = """你是{lawyer_name}，{style}

请根据以下法条，生成一个针对娱乐行业（网红、明星、带货主播、MCN机构）的法律问答卡片。

要求：
1. 问题：一个具体的、贴近真实业务场景的法律问题（15-30字）
2. 答案：专业法律分析，引用具体法条名称和条款号，200-350字。要把法律术语翻译成当事人听得懂的大白话，但保持专业准确
3. 法条依据：列出涉及的法律法规名称（如《民法典》《消费者权益保护法》）
4. 律师点评：一句话犀利收尾（15-40字），有冲击力，让人想转发朋友圈

重要：输出纯文本，不要使用任何 markdown 格式（不要用 **加粗**、*斜体*、# 标题等），因为内容将直接渲染到图片上。

请严格按以下 JSON 格式输出，不要输出任何其他内容：
{{"question": "...", "answer": "...", "law_refs": "...", "comment": "..."}}

参考法条：
{law_text}"""

QA_PROMPT_WITH_SYSTEM = """{system_prompt}

请根据以下法条，生成一个完整的法律问答卡片（适合做成朋友圈图片）。

要求：
1. 问题：一个具体的、贴近娱乐行业真实业务场景的法律问题（15-30字）
2. 答案：专业法律分析，引用具体法条名称和条款号，200-350字
3. 法条依据：列出涉及的法律法规名称
4. 律师点评：一句话犀利收尾（15-40字），有冲击力，让人想转发朋友圈

重要：输出纯文本，不要使用任何 markdown 格式（不要用 **加粗**、*斜体*、# 标题等），因为内容将直接渲染到图片上。

请严格按以下 JSON 格式输出，不要输出任何其他内容：
{{"question": "...", "answer": "...", "law_refs": "...", "comment": "..."}}

参考法条：
{law_text}"""


def generate_qa(law_text: str) -> dict:
    """用 Gemini 生成完整的法律问答卡片"""
    try:
        if PERSONA_SYSTEM_PROMPT:
            prompt = QA_PROMPT_WITH_SYSTEM.format(
                system_prompt=PERSONA_SYSTEM_PROMPT, law_text=law_text
            )
        else:
            prompt = QA_PROMPT_TEMPLATE.format(
                lawyer_name=LAWYER_NAME, style=style_desc, law_text=law_text
            )
        resp = client.models.generate_content(model="gemini-2.5-flash", contents=[prompt])
        text = resp.text.strip()
        # 提取 JSON（可能被 ```json 包裹）
        if "```" in text:
            import re
            m = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
            if m:
                text = m.group(1)
        qa = _json.loads(text)
        return {
            "question": qa.get("question", ""),
            "answer": qa.get("answer", ""),
            "law_refs": qa.get("law_refs", ""),
            "comment": qa.get("comment", ""),
        }
    except Exception as e:
        print(f"  问答生成失败: {e}")
        return {
            "question": "这条法律你了解吗？",
            "answer": law_text,
            "law_refs": "",
            "comment": "了解法律，是保护自己权益的第一步。",
        }


print("正在获取今日法条...")
law_articles = get_law_articles(3)

print("正在生成今日法律问答...")
CASES = []
for law in law_articles:
    qa = generate_qa(law)
    print(f"  问: {qa['question']}")
    print(f"  答: {qa['answer'][:60]}...")
    print(f"  法条: {qa['law_refs']}")
    print(f"  点评: {qa['comment']}\n")
    CASES.append(qa)

# ── Step 3: 通过模板生成图片 ──────────────────────────────
portrait_part = None
if PORTRAIT_PATH.exists():
    portrait_bytes = PORTRAIT_PATH.read_bytes()
    portrait_part = types.Part.from_bytes(data=portrait_bytes, mime_type="image/png")
    print(f"已加载真人照片参考图：{PORTRAIT_PATH}")
else:
    print("警告：未找到 portrait_cutout.png，将使用 AI 生成虚拟人像")

# 构建模板配置
template_config = {
    "lawyer_name": LAWYER_NAME,
    "license_number": LICENSE_NUMBER,
    "portrait_path": PORTRAIT_PATH if PORTRAIT_PATH.exists() else None,
    "portrait_part": portrait_part,
    "gemini_client": client,
    "skill_dir": SKILL_DIR,
}

for i, case in enumerate(CASES, 1):
    print(f"\n正在生成第 {i}/3 张图片...")
    out_path = OUTPUT_DIR / f"poster_{i:02d}.png"

    success = template.generate_poster(case, template_config, out_path)
    if not success:
        print(f"  第 {i} 张生成失败")

print("\n全部完成！图片保存在：", OUTPUT_DIR)
