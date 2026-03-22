#!/usr/bin/env python3
"""
视频生成脚本 - 使用火山引擎Seedance 1.5 pro生成单个视频片段
用法: python generate_video.py --prompt "描述" --duration 5 [--first-frame url] [--output clip.mp4]
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

def create_video_task(prompt: str, duration: int = 5, generate_audio: bool = True,
                      first_frame_url: str = None, resolution: str = "720p",
                      ratio: str = "16:9") -> str:
    """创建视频生成任务，返回任务ID"""

    api_key = get_api_key()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    content = [{"type": "text", "text": prompt}]

    # 如果有首帧图片
    if first_frame_url:
        content.append({
            "type": "image_url",
            "image_url": {"url": first_frame_url},
            "role": "first_frame"
        })
        ratio = "adaptive"  # 使用首帧时自动适配比例

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
        print(f"错误: API调用失败 ({response.status_code})")
        print(response.text)
        sys.exit(1)

    result = response.json()
    return result["id"]

def query_task(task_id: str) -> dict:
    """查询任务状态"""

    api_key = get_api_key()
    headers = {"Authorization": f"Bearer {api_key}"}

    response = requests.get(
        f"{BASE_URL}/contents/generations/tasks/{task_id}",
        headers=headers
    )

    if response.status_code != 200:
        print(f"错误: 查询失败 ({response.status_code})")
        sys.exit(1)

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
            print(f"错误: 视频生成失败")
            print(f"  错误码: {error.get('code')}")
            print(f"  错误信息: {error.get('message')}")
            sys.exit(1)
        elif status in ["queued", "running"]:
            print(".", end="", flush=True)
            time.sleep(5)
        else:
            print(f"错误: 未知状态 {status}")
            sys.exit(1)

    print(f"\n错误: 视频生成超时 ({timeout}秒)")
    sys.exit(1)

def download_video(url: str, output_path: str):
    """下载视频文件"""

    response = requests.get(url, stream=True)
    if response.status_code != 200:
        print(f"错误: 下载失败 ({response.status_code})")
        sys.exit(1)

    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

def generate_video(prompt: str, duration: int = 5, generate_audio: bool = True,
                   first_frame_url: str = None, resolution: str = "720p",
                   ratio: str = "16:9", output_path: str = None) -> dict:
    """生成视频的完整流程"""

    print(f"创建视频生成任务...")
    print(f"  Prompt: {prompt[:50]}...")
    print(f"  时长: {duration}秒")
    print(f"  分辨率: {resolution}")
    print(f"  比例: {ratio}")
    print(f"  有声: {generate_audio}")

    task_id = create_video_task(
        prompt=prompt,
        duration=duration,
        generate_audio=generate_audio,
        first_frame_url=first_frame_url,
        resolution=resolution,
        ratio=ratio
    )

    print(f"任务ID: {task_id}")
    print("等待生成完成", end="")

    result = wait_for_video(task_id)
    print()

    video_url = result["content"]["video_url"]
    last_frame_url = result["content"].get("last_frame_url")

    print(f"视频生成成功!")
    print(f"  视频URL: {video_url}")
    if last_frame_url:
        print(f"  尾帧URL: {last_frame_url}")

    # 下载视频
    if output_path:
        print(f"正在下载视频...")
        download_video(video_url, output_path)
        print(f"视频已保存到: {output_path}")

    return {
        "task_id": task_id,
        "video_url": video_url,
        "last_frame_url": last_frame_url,
        "output_path": output_path
    }

def main():
    parser = argparse.ArgumentParser(description='生成单个视频片段')
    parser.add_argument('--prompt', '-p', required=True, help='视频描述prompt')
    parser.add_argument('--duration', '-d', type=int, default=5,
                        help='视频时长(4-12秒)，默认5秒')
    parser.add_argument('--first-frame', '-f', help='首帧图片URL')
    parser.add_argument('--resolution', '-r', default='720p',
                        choices=['480p', '720p', '1080p'], help='分辨率')
    parser.add_argument('--ratio', default='16:9',
                        choices=['16:9', '9:16', '1:1', '4:3', '3:4'],
                        help='宽高比')
    parser.add_argument('--no-audio', action='store_true', help='不生成音频')
    parser.add_argument('--output', '-o', help='输出视频文件路径')

    args = parser.parse_args()

    result = generate_video(
        prompt=args.prompt,
        duration=args.duration,
        generate_audio=not args.no_audio,
        first_frame_url=args.first_frame,
        resolution=args.resolution,
        ratio=args.ratio,
        output_path=args.output
    )

    # 输出JSON结果供后续使用
    print("\n=== 结果JSON ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
