#!/usr/bin/env python3
"""
批量视频生成脚本 - 根据脚本JSON批量生成视频片段，使用尾帧接首帧保证连贯性
用法: python generate_all.py --script script.json --output-dir ./clips
"""

import os
import sys
import json
import time
import argparse
import requests
from pathlib import Path

BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"

def load_config():
    """从项目根目录的config.js读取配置"""
    current_dir = Path(__file__).resolve().parent

    # 向上查找config.js
    for parent in [current_dir] + list(current_dir.parents):
        config_path = parent / "config.js"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                for line in content.split('\n'):
                    if 'ARK_API_KEY:' in line and 'process.env' in line:
                        # 先尝试环境变量
                        api_key = os.getenv('ARK_API_KEY')
                        if api_key:
                            return api_key
                        # 提取默认值
                        if "'" in line:
                            parts = line.split("'")
                            if len(parts) >= 2:
                                default_key = parts[-2]
                                if default_key and default_key != 'YOUR_ARK_API_KEY':
                                    return default_key
            break

    return os.getenv('ARK_API_KEY')

def get_api_key():
    api_key = load_config()
    if not api_key:
        print("错误: 未找到ARK_API_KEY")
        print("请在项目根目录的config.js中配置，或设置环境变量 ARK_API_KEY")
        sys.exit(1)
    return api_key

def create_video_task(prompt: str, duration: int, generate_audio: bool = True,
                      first_frame_url: str = None, resolution: str = "720p",
                      ratio: str = "16:9") -> str:
    """创建视频生成任务"""

    api_key = get_api_key()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    content = [{"type": "text", "text": prompt}]

    if first_frame_url:
        content.append({
            "type": "image_url",
            "image_url": {"url": first_frame_url},
            "role": "first_frame"
        })
        ratio = "adaptive"

    payload = {
        "model": "doubao-seedance-1-5-pro-251215",
        "content": content,
        "resolution": resolution,
        "ratio": ratio,
        "duration": duration,
        "generate_audio": generate_audio,
        "watermark": False,
        "return_last_frame": True
    }

    response = requests.post(
        f"{BASE_URL}/contents/generations/tasks",
        headers=headers,
        json=payload
    )

    if response.status_code != 200:
        raise Exception(f"API调用失败: {response.status_code} - {response.text}")

    return response.json()["id"]

def query_task(task_id: str) -> dict:
    """查询任务状态"""

    api_key = get_api_key()
    headers = {"Authorization": f"Bearer {api_key}"}

    response = requests.get(
        f"{BASE_URL}/contents/generations/tasks/{task_id}",
        headers=headers
    )

    return response.json()

def wait_for_video(task_id: str, timeout: int = 300) -> dict:
    """等待视频生成完成"""

    start_time = time.time()
    while time.time() - start_time < timeout:
        result = query_task(task_id)
        status = result.get("status")

        if status == "succeeded":
            return result
        elif status == "failed":
            error = result.get("error", {})
            raise Exception(f"生成失败: {error.get('message', '未知错误')}")
        elif status in ["queued", "running"]:
            time.sleep(5)
        else:
            raise Exception(f"未知状态: {status}")

    raise Exception(f"生成超时 ({timeout}秒)")

def download_video(url: str, output_path: str):
    """下载视频"""

    response = requests.get(url, stream=True)
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

def generate_all_videos(script_path: str, output_dir: str, resolution: str = "720p",
                        ratio: str = "16:9", generate_audio: bool = True,
                        first_frame: str = None) -> list:
    """批量生成所有视频片段

    Args:
        script_path: 脚本JSON文件路径
        output_dir: 输出目录
        resolution: 分辨率
        ratio: 宽高比
        generate_audio: 是否生成音频
        first_frame: 首帧图片URL或路径（可选，用于第一个片段）
    """

    # 读取脚本
    with open(script_path, 'r', encoding='utf-8') as f:
        script = json.load(f)

    scenes = script.get("scenes", [])
    if not scenes:
        print("错误: 脚本中没有scenes")
        sys.exit(1)

    # 使用脚本中的参数（如果有）
    resolution = script.get("resolution", resolution)
    ratio = script.get("ratio", ratio)
    generate_audio = script.get("generate_audio", generate_audio)
    first_frame = script.get("first_frame", first_frame)

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    print(f"开始生成 {len(scenes)} 个视频片段")
    print(f"  分辨率: {resolution}")
    print(f"  比例: {ratio}")
    print(f"  有声: {generate_audio}")
    if first_frame:
        print(f"  首帧: {first_frame}")
    print()

    results = []
    last_frame_url = None

    for i, scene in enumerate(scenes):
        prompt = scene.get("prompt", "")
        duration = scene.get("duration", 5)

        print(f"[{i+1}/{len(scenes)}] 生成片段...")
        print(f"  Prompt: {prompt[:50]}...")
        print(f"  时长: {duration}秒")

        try:
            # 第一个片段：如果提供了首帧则用图生视频，否则用文生视频
            # 后续片段：使用上一个片段的尾帧作为首帧
            if i == 0 and first_frame:
                # 用户提供的首帧图片
                task_id = create_video_task(
                    prompt=prompt,
                    duration=duration,
                    generate_audio=generate_audio,
                    first_frame_url=first_frame,
                    resolution=resolution,
                    ratio=ratio
                )
            elif i == 0:
                # 文生视频
                task_id = create_video_task(
                    prompt=prompt,
                    duration=duration,
                    generate_audio=generate_audio,
                    resolution=resolution,
                    ratio=ratio
                )
            else:
                # 尾帧接首帧
                task_id = create_video_task(
                    prompt=prompt,
                    duration=duration,
                    generate_audio=generate_audio,
                    first_frame_url=last_frame_url,
                    resolution=resolution,
                    ratio=ratio
                )

            print(f"  任务ID: {task_id}")
            print("  等待生成...", end="", flush=True)

            result = wait_for_video(task_id)
            print(" 完成!")

            video_url = result["content"]["video_url"]
            last_frame_url = result["content"].get("last_frame_url")

            # 下载视频
            output_path = os.path.join(output_dir, f"clip_{i:02d}.mp4")
            print(f"  下载中...")
            download_video(video_url, output_path)
            print(f"  已保存: {output_path}")

            results.append({
                "index": i,
                "prompt": prompt,
                "duration": duration,
                "video_url": video_url,
                "last_frame_url": last_frame_url,
                "output_path": output_path
            })

        except Exception as e:
            print(f"  错误: {e}")
            results.append({
                "index": i,
                "prompt": prompt,
                "error": str(e)
            })

        print()

    # 保存结果
    result_path = os.path.join(output_dir, "results.json")
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # 生成filelist.txt供FFmpeg使用
    filelist_path = os.path.join(output_dir, "filelist.txt")
    with open(filelist_path, 'w') as f:
        for r in results:
            if "output_path" in r:
                filename = os.path.basename(r["output_path"])
                f.write(f"file '{filename}'\n")

    print("=" * 50)
    print(f"生成完成!")
    print(f"  成功: {len([r for r in results if 'output_path' in r])}/{len(scenes)}")
    print(f"  结果: {result_path}")
    print(f"  文件列表: {filelist_path}")
    print()
    print("使用以下命令拼接视频:")
    print(f"  cd {output_dir} && ffmpeg -f concat -safe 0 -i filelist.txt -c copy output.mp4")

    return results

def main():
    parser = argparse.ArgumentParser(description='批量生成视频片段')
    parser.add_argument('--script', '-s', required=True, help='脚本JSON文件路径')
    parser.add_argument('--output-dir', '-o', default='./clips', help='输出目录')
    parser.add_argument('--resolution', '-r', default='720p',
                        choices=['480p', '720p', '1080p'], help='分辨率')
    parser.add_argument('--ratio', default='16:9',
                        choices=['16:9', '9:16', '1:1'], help='宽高比')
    parser.add_argument('--no-audio', action='store_true', help='不生成音频')
    parser.add_argument('--first-frame', '-f', help='首帧图片URL或路径（用于第一个片段）')

    args = parser.parse_args()

    generate_all_videos(
        script_path=args.script,
        output_dir=args.output_dir,
        resolution=args.resolution,
        ratio=args.ratio,
        generate_audio=not args.no_audio,
        first_frame=args.first_frame
    )

if __name__ == '__main__':
    main()
