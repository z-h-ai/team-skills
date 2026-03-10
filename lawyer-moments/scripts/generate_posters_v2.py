"""
律师每日朋友圈配图生成器 - 优化版
1. 支持 Agent 联网搜索法条
2. 并行生成图片（加速）
3. 自动发送到飞书
"""
import os
import sys
import json
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from google import genai
from google.genai import types

sys.path.insert(0, str(Path(__file__).parent))
from fetch_law import get_law_articles

SKILL_DIR = Path(__file__).parent.parent
PERSONA_PATH = SKILL_DIR / "inputs" / "persona.md"
PORTRAIT_PATH = SKILL_DIR / "inputs" / "portrait_cutout.png"
OUTPUT_DIR = SKILL_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

sys.path.insert(0, str(SKILL_DIR))
from templates import get_template

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
GEMINI_API_KEY = cfg.get("gemini_api_key", os.environ.get("GEMINI_API_KEY", ""))

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

if not GEMINI_API_KEY:
    print("错误：请在 inputs/persona.md 中填写 gemini_api_key")
    sys.exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)
template = get_template(TEMPLATE_NAME)
print(f"模板: {template.TEMPLATE_INFO['display_name']}\n")
