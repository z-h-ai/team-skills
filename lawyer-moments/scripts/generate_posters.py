"""
律师每日朋友圈配图生成器 - 优化版
优化点：
1. 跳过 Playwright 爬取，直接用内置法条
2. 并行生成 3 张图片
3. 固定最快模型
4. 法条缓存
"""
import os
import sys
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from google import genai
from google.genai import types

sys.path.insert(0, str(Path(__file__).parent))
from fetch_law import get_law_articles

# ── 路径 ──────────────────────────────────────────────────
SKILL_DIR = Path(__file__).parent.parent
PERSONA_PATH = SKILL_DIR / "inputs" / "persona.md"
PORTRAIT_PATH = SKILL_DIR / "inputs" / "portrait_cutout.png"
OUTPUT_DIR = SKILL_DIR / "output"
CACHE_PATH = SKILL_DIR / "inputs" / "law_cache.json"
OUTPUT_DIR.mkdir(exist_ok=True)

sys.path.insert(0, str(SKILL_DIR))
from templates import get_template

# ── 读取配置 ──────────────────────────────────────────────
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
TEMPLATE_NAME = cfg.get("template", "classic")
# 优先从环境变量读取 API Key，避免硬编码
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", cfg.get("gemini_api_key", ""))
PREFERRED_MODEL = cfg.get("preferred_model", "gemini-3-pro-image-preview")

# 加载 persona
PERSONA_FILE = cfg.get("persona_file", "")
PERSONA_SYSTEM_PROMPT = None

if PERSONA_FILE:
    persona_file_path = SKILL_DIR / "inputs" / PERSONA_FILE
    if persona_file_path.exists():
        import re
        content = persona_file_path.read_text(encoding="utf-8")
        code_blocks = re.findall(r'```\n(.*?)```', content, re.DOTALL)
        if code_blocks:
            PERSONA_SYSTEM_PROMPT = code_blocks[0].strip()
        persona_match = re.search(r'^persona:\s*(.+)$', content, re.MULTILINE)
        PERSONA = persona_match.group(1).strip() if persona_match else cfg.get("persona", "专业严谨")
    else:
        PERSONA = cfg.get("persona", "专业严谨")
else:
    PERSONA = cfg.get("persona", "专业严谨")

if not GEMINI_API_KEY:
    print("错误：请设置环境变量 GEMINI_API_KEY 或在 inputs/persona.md 中填写 gemini_api_key")
    sys.exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)

# 加载模板
template = get_template(TEMPLATE_NAME)
print(f"模板: {template.TEMPLATE_INFO['display_name']}\n")

# ── 法条缓存 ──────────────────────────────────────────────
def load_cache():
    if CACHE_PATH.exists():
        try:
            data = json.loads(CACHE_PATH.read_text())
            import time
            if time.time() - data.get("timestamp", 0) < 86400:  # 24h
                return data.get("articles", [])
        except:
            pass
    return None

def save_cache(articles):
    import time
    CACHE_PATH.write_text(json.dumps({
        "timestamp": time.time(),
        "articles": articles
    }, ensure_ascii=False))

# ── 生成问答 ──────────────────────────────────────────────
PERSONA_STYLE_MAP = {
    "接地气幽默": "用接地气、幽默风趣的语言，像朋友聊天一样",
    "毒蛇犀利": "用犀利毒舌的风格，一针见血",
    "温和专业": "用温和、专业、有权威感的语言",
}
style_desc = PERSONA_STYLE_MAP.get(PERSONA, PERSONA)

QA_PROMPT = """你是{lawyer_name}，{style}

生成娱乐行业法律问答卡片（网红/MCN/主播）。

JSON格式输出：
{{"question": "...", "answer": "...", "law_refs": "...", "comment": "..."}}

参考法条：{law_text}"""

def generate_qa(law_text: str) -> dict:
    try:
        if PERSONA_SYSTEM_PROMPT:
            prompt = f"{PERSONA_SYSTEM_PROMPT}\n\n{QA_PROMPT.format(lawyer_name=LAWYER_NAME, style=style_desc, law_text=law_text)}"
        else:
            prompt = QA_PROMPT.format(lawyer_name=LAWYER_NAME, style=style_desc, law_text=law_text)
        
        resp = client.models.generate_content(model="gemini-2.5-flash", contents=[prompt])
        text = resp.text.strip()
        
        if "```" in text:
            import re
            m = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
            if m:
                text = m.group(1)
        
        return json.loads(text)
    except Exception as e:
        print(f"  问答生成失败: {e}")
        return {
            "question": "这条法律你了解吗？",
            "answer": law_text,
            "law_refs": "",
            "comment": "了解法律，保护自己。",
        }

# ── 并行生成图片 ──────────────────────────────────────────
def generate_single_poster(args):
    i, case, template_config = args
    out_path = OUTPUT_DIR / f"poster_{i:02d}.png"
    print(f"生成第 {i}/3 张...")
    success = template.generate_poster(case, template_config, out_path)
    return i, success

# ── 主流程 ──────────────────────────────────────────────
print("获取法条...")
cached = load_cache()
if cached:
    law_articles = cached[:3]
    print(f"使用缓存法条 ({len(law_articles)} 条)")
else:
    law_articles = get_law_articles(3)
    save_cache(law_articles)
    print(f"获取新法条 ({len(law_articles)} 条)")

print("\n生成问答...")
CASES = []
for law in law_articles:
    qa = generate_qa(law)
    print(f"  ✓ {qa['question'][:30]}...")
    CASES.append(qa)

# 准备模板配置
portrait_part = None
if PORTRAIT_PATH.exists():
    portrait_bytes = PORTRAIT_PATH.read_bytes()
    portrait_part = types.Part.from_bytes(data=portrait_bytes, mime_type="image/png")

template_config = {
    "lawyer_name": LAWYER_NAME,
    "license_number": LICENSE_NUMBER,
    "portrait_path": PORTRAIT_PATH if PORTRAIT_PATH.exists() else None,
    "portrait_part": portrait_part,
    "gemini_client": client,
    "skill_dir": SKILL_DIR,
    "preferred_model": PREFERRED_MODEL,  # 新增：固定模型
}

# 并行生成图片
print("\n并行生成图片...")
with ThreadPoolExecutor(max_workers=3) as executor:
    tasks = [(i, case, template_config) for i, case in enumerate(CASES, 1)]
    results = list(executor.map(generate_single_poster, tasks))

success_count = sum(1 for _, success in results if success)
print(f"\n完成！成功 {success_count}/3 张，保存在: {OUTPUT_DIR}")

# 自动发送到飞书
if success_count > 0:
    print("\n发送到飞书...")
    for i in range(1, success_count + 1):
        img_path = OUTPUT_DIR / f"poster_{i:02d}.png"
        if img_path.exists():
            # 输出特殊标记，让 Agent 识别并发送
            print(f"SEND_TO_FEISHU:{img_path}")
