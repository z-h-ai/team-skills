#!/usr/bin/env python3
"""
视频分析脚本 - 上传视频并使用火山引擎视频理解API分析
用法: python analyze_video.py <video_path> [--fps 5] [--output output.json]
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path


def generate_scenes_from_structure(structure, transcription=None):
    """
    将 structure 转换为 scenes 格式，供 ai-video-generator 直接使用
    """
    scenes = []
    
    for section_data in structure:
        section = section_data.get('section', '')
        
        # 处理单场景部分（黄金3秒、冲突设置、反转高潮、CTA引导）
        if section in ['黄金3秒', '冲突设置', '反转高潮', 'CTA引导']:
            scene_desc = section_data.get('scene', '')
            dialogue = section_data.get('dialogue', '')
            shot_type = section_data.get('shot_type', '中景')
            time_range = section_data.get('time_range', '')
            
            # 计算 duration
            duration = calculate_duration(time_range)
            
            # 构建 prompt
            prompt = build_prompt(scene_desc, dialogue, shot_type)
            
            if prompt:
                scenes.append({
                    'prompt': prompt,
                    'duration': duration
                })
        
        # 处理多场景部分（内容展开）
        elif section == '内容展开':
            sub_scenes = section_data.get('scenes', [])
            for sub_scene in sub_scenes:
                scene_desc = sub_scene.get('scene', '')
                dialogue = sub_scene.get('dialogue', '')
                shot_type = sub_scene.get('shot_type', '中景')
                time_range = sub_scene.get('time', '')
                
                duration = calculate_duration(time_range)
                prompt = build_prompt(scene_desc, dialogue, shot_type)
                
                if prompt:
                    scenes.append({
                        'prompt': prompt,
                        'duration': duration
                    })
    
    return scenes


def calculate_duration(time_range):
    """
    从时间范围计算 duration
    例如: "0-3秒" → 3, "8-20秒" → 12
    """
    if not time_range:
        return 5  # 默认5秒
    
    try:
        # 移除"秒"字符
        time_range = time_range.replace('秒', '')
        
        # 分割时间范围
        if '-' in time_range:
            parts = time_range.split('-')
            start = float(parts[0])
            end = float(parts[1])
            return int(end - start)
        else:
            return 5
    except:
        return 5


def build_prompt(scene_desc, dialogue, shot_type):
    """
    构建 prompt: 人物描述 + 说："台词内容" + 表情/动作 + 景别
    
    示例:
    - 输入: scene="职场女性对着镜头", dialogue="这3个技巧", shot_type="特写"
    - 输出: "职场女性对着镜头说："这3个技巧"，特写镜头"
    """
    if not scene_desc:
        return ""
    
    prompt_parts = []
    
    # 处理场景描述和台词
    if dialogue:
        # 检查 scene_desc 是否已经包含台词
        if dialogue in scene_desc:
            # 场景描述已包含台词，直接使用
            prompt_parts.append(scene_desc)
        else:
            # 需要添加台词
            # 检查是否已经有"说"或"讲"等动词
            if '说' in scene_desc or '讲' in scene_desc or '表示' in scene_desc:
                # 已有动词，直接插入台词
                prompt_parts.append(f'{scene_desc}："{dialogue}"')
            else:
                # 没有动词，添加"说"
                prompt_parts.append(f'{scene_desc}说："{dialogue}"')
    else:
        # 没有台词，直接使用场景描述
        prompt_parts.append(scene_desc)
    
    # 添加景别
    shot_type_mapping = {
        '特写': '特写镜头',
        '中景': '中景',
        '全景': '全景',
        '近景': '近景',
        '远景': '远景'
    }
    shot_desc = shot_type_mapping.get(shot_type, shot_type)
    
    # 检查景别是否已经在描述中
    if shot_desc and shot_desc not in prompt_parts[0]:
        prompt_parts.append(shot_desc)
    
    return '，'.join(prompt_parts)


def load_config():
    """从项目根目录的config.js读取配置"""
    # 查找项目根目录的config.js
    current_dir = Path(__file__).resolve().parent

    # 向上查找config.js
    for parent in [current_dir] + list(current_dir.parents):
        config_path = parent / "config.js"
        if config_path.exists():
            # 读取config.js并提取ARK_API_KEY
            with open(config_path, "r", encoding="utf-8") as f:
                content = f.read()
                # 简单解析：查找ARK_API_KEY的值
                for line in content.split("\n"):
                    if "ARK_API_KEY:" in line and "process.env" in line:
                        # 先尝试环境变量
                        api_key = os.getenv("ARK_API_KEY")
                        if api_key:
                            return api_key
                        # 提取默认值
                        if "'" in line:
                            parts = line.split("'")
                            if len(parts) >= 2:
                                default_key = parts[-2]
                                if default_key and default_key != "YOUR_ARK_API_KEY":
                                    return default_key
            break

    # 如果config.js中没找到，尝试环境变量
    return os.getenv("ARK_API_KEY")


def check_dependencies():
    try:
        from volcenginesdkarkruntime import Ark

        return True
    except ImportError:
        print("错误: 请先安装依赖: pip install volcengine-python-sdk[ark]")
        sys.exit(1)


def analyze_video(video_path: str, fps: float = 5.0, output_path: str = None, enable_transcription: bool = False):
    """分析视频并输出结构化脚本模板"""

    from volcenginesdkarkruntime import Ark
    import subprocess

    # 从config.js读取API Key
    api_key = load_config()
    if not api_key:
        print("错误: 未找到ARK_API_KEY")
        print("请在项目根目录的config.js中配置，或设置环境变量 ARK_API_KEY")
        sys.exit(1)

    # 检查视频文件
    if not os.path.exists(video_path):
        print(f"错误: 视频文件不存在: {video_path}")
        sys.exit(1)

    # 检查文件大小 (≤512MB for Files API)
    file_size = os.path.getsize(video_path) / (1024 * 1024)
    if file_size > 512:
        print(f"错误: 视频文件过大 ({file_size:.1f}MB)，最大支持512MB")
        sys.exit(1)

    print(f"视频文件: {video_path} ({file_size:.1f}MB)")

    # 获取视频尺寸和比例
    try:
        cmd = [
            'ffprobe', '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height,duration',
            '-of', 'json',
            video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            video_info = json.loads(result.stdout)
            if 'streams' in video_info and len(video_info['streams']) > 0:
                stream = video_info['streams'][0]
                width = stream.get('width', 0)
                height = stream.get('height', 0)
                duration = float(stream.get('duration', 0))

                # 计算比例
                if width > 0 and height > 0:
                    aspect_ratio = width / height
                    if 1.7 <= aspect_ratio <= 1.8:
                        ratio = "16:9"
                    elif 0.55 <= aspect_ratio <= 0.6:
                        ratio = "9:16"
                    elif 0.95 <= aspect_ratio <= 1.05:
                        ratio = "1:1"
                    else:
                        ratio = f"{width}:{height}"

                    print(f"视频尺寸: {width}x{height} ({ratio})")
                    print(f"视频时长: {duration:.1f}秒")
                else:
                    width, height, ratio, duration = 0, 0, "16:9", 0
            else:
                width, height, ratio, duration = 0, 0, "16:9", 0
        else:
            print("警告: 无法获取视频尺寸，使用默认值 16:9")
            width, height, ratio, duration = 0, 0, "16:9", 0
    except Exception as e:
        print(f"警告: 获取视频信息失败 ({e})，使用默认值 16:9")
        width, height, ratio, duration = 0, 0, "16:9", 0

    # 初始化客户端
    client = Ark(base_url="https://ark.cn-beijing.volces.com/api/v3", api_key=api_key)

    # 步骤1: 上传视频
    print(f"正在上传视频 (fps={fps})...")
    with open(video_path, "rb") as f:
        file = client.files.create(
            file=f, purpose="user_data", preprocess_configs={"video": {"fps": fps}}
        )
    print(f"上传成功，文件ID: {file.id}")

    # 步骤2: 等待处理完成
    print("等待视频处理", end="", flush=True)
    while file.status == "processing":
        time.sleep(2)
        file = client.files.retrieve(file.id)
        print(".", end="", flush=True)
    print()

    if file.status not in ["processed", "active"]:
        print(f"错误: 视频处理失败，状态: {file.status}")
        sys.exit(1)

    print("视频处理完成")

    # 步骤3: 调用视频理解API
    print("正在分析视频内容...")

    analysis_prompt = """请分析这个短视频，按以下JSON格式输出：
{
  "duration": 视频总时长（秒，数字）,
  "width": 视频宽度（像素）,
  "height": 视频高度（像素）,
  "ratio": "视频比例（16:9/9:16/1:1）",
  "type": "视频类型（知识分享/口播/剧情/产品展示）",
  "topic": "视频主题",
  "structure": [
    {
      "section": "黄金3秒",
      "time_range": "0-3秒",
      "scene": "画面描述",
      "dialogue": "台词内容（如有）",
      "shot_type": "景别（特写/中景/全景）",
      "purpose": "作用分析"
    },
    {
      "section": "冲突设置",
      "time_range": "3-8秒",
      "scene": "画面描述",
      "dialogue": "台词内容",
      "shot_type": "景别",
      "purpose": "作用分析"
    },
    {
      "section": "内容展开",
      "time_range": "8-50秒",
      "scenes": [
        {"time": "8-20秒", "scene": "画面描述", "dialogue": "台词", "shot_type": "景别"},
        {"time": "20-35秒", "scene": "画面描述", "dialogue": "台词", "shot_type": "景别"},
        {"time": "35-50秒", "scene": "画面描述", "dialogue": "台词", "shot_type": "景别"}
      ]
    },
    {
      "section": "反转高潮",
      "time_range": "50-55秒",
      "scene": "画面描述",
      "dialogue": "台词内容",
      "shot_type": "景别",
      "purpose": "作用分析"
    },
    {
      "section": "CTA引导",
      "time_range": "55-60秒",
      "scene": "画面描述",
      "dialogue": "台词内容",
      "shot_type": "景别",
      "purpose": "作用分析"
    }
  ],
  "reusable_template": {
    "hook": "黄金3秒台词模板，用[]标注可替换部分",
    "conflict": "冲突设置台词模板",
    "content_points": ["要点1模板", "要点2模板", "要点3模板"],
    "climax": "反转高潮台词模板",
    "cta": "CTA台词模板"
  }
}

请根据视频实际内容填写，如果视频时长不足60秒，请根据实际时长调整各部分的时间范围。"""

    response = client.responses.create(
        model="doubao-seed-1-8-251228",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_video", "file_id": file.id},
                    {"type": "input_text", "text": analysis_prompt},
                ],
            }
        ],
    )

    result_text = response.output[1].content[0].text

    # 尝试解析JSON
    try:
        # 查找JSON部分
        start = result_text.find("{")
        end = result_text.rfind("}") + 1
        if start != -1 and end > start:
            json_str = result_text[start:end]
            result = json.loads(json_str)

            # 添加检测到的视频尺寸信息（如果API没有返回）
            if width > 0 and height > 0:
                if 'width' not in result or result.get('width') == 0:
                    result['width'] = width
                if 'height' not in result or result.get('height') == 0:
                    result['height'] = height
                if 'ratio' not in result or not result.get('ratio'):
                    result['ratio'] = ratio
        else:
            result = {"raw_analysis": result_text}
            if width > 0 and height > 0:
                result['width'] = width
                result['height'] = height
                result['ratio'] = ratio
    except json.JSONDecodeError:
        result = {"raw_analysis": result_text}
        if width > 0 and height > 0:
            result['width'] = width
            result['height'] = height
            result['ratio'] = ratio

    # 步骤4: 音频转录（可选）
    transcription_data = None
    if enable_transcription:
        print("\n正在提取音频对白...")
        try:
            from transcribe_audio import transcribe_video
            transcription = transcribe_video(video_path, output_path=None)
            if transcription and 'result' in transcription:
                result['transcription'] = transcription['result']
                transcription_data = transcription['result']
                print("✅ 音频转录完成")
        except Exception as e:
            print(f"⚠️  音频转录失败: {e}")
            result['transcription'] = None

    # 步骤5: 生成 scenes 字段（供 ai-video-generator 直接使用）
    if 'structure' in result:
        print("\n正在生成 scenes 字段...")
        try:
            scenes = generate_scenes_from_structure(result['structure'], transcription_data)
            if scenes:
                result['scenes'] = scenes
                result['resolution'] = '720p'
                result['generate_audio'] = True
                print(f"✅ 已生成 {len(scenes)} 个场景")
        except Exception as e:
            print(f"⚠️  生成 scenes 失败: {e}")

    # 输出结果
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 分析结果已保存到: {output_path}")
    else:
        print("\n=== 分析结果 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    return result


def main():
    parser = argparse.ArgumentParser(description="分析短视频，提取脚本模板")
    parser.add_argument("video_path", help="视频文件路径")
    parser.add_argument(
        "--fps", type=float, default=5.0, help="抽帧频率 (0.2-5)，默认5"
    )
    parser.add_argument("--output", "-o", help="输出JSON文件路径")
    parser.add_argument(
        "--transcribe", "-t", action="store_true", help="启用音频转录提取对白"
    )

    args = parser.parse_args()

    check_dependencies()
    analyze_video(args.video_path, args.fps, args.output, args.transcribe)


if __name__ == "__main__":
    main()
