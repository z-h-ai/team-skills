#!/usr/bin/env python3
"""
首尾帧生成脚本 - 使用火山引擎Seedream 4.5生成首尾帧图片
用法: python generate_keyframes.py --prompt "产品展示" --output-dir ./keyframes
"""

import os
import sys
import json
import time
import argparse
import requests
from pathlib import Path

def load_config():
    """从项目根目录的config.js读取配置"""
    current_dir = Path(__file__).resolve().parent
    for parent in [current_dir] + list(current_dir.parents):
        config_path = parent / "config.js"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                for line in content.split('\n'):
                    if 'ARK_API_KEY:' in line and 'process.env' in line:
                        api_key = os.getenv('ARK_API_KEY')
                        if api_key:
                            return api_key
                        if "'" in line:
                            parts = line.split("'")
                            if len(parts) >= 2:
                                default_key = parts[-2]
                                if default_key and default_key != 'YOUR_ARK_API_KEY':
                                    return default_key
            break
    return os.getenv('ARK_API_KEY')

def generate_image(prompt, reference_image=None, size="2560x1440", output_path=None):
    """
    使用Seedream 4.5生成图片

    Args:
        prompt: 图片描述
        reference_image: 参考图片URL或路径（可选）
        size: 图片尺寸，如"2560x1440"（16:9）或"2K"/"4K"
        output_path: 输出文件路径

    Returns:
        图片URL或保存的文件路径
    """
    api_key = load_config()
    if not api_key:
        print("错误: 未找到ARK_API_KEY")
        sys.exit(1)

    url = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "doubao-seedream-4.5",
        "prompt": prompt,
        "size": size,
        "response_format": "url",
        "watermark": False
    }

    # 如果提供了参考图片，添加到请求中
    if reference_image:
        if reference_image.startswith('http'):
            payload["image"] = reference_image
        else:
            # 本地文件，转换为base64
            import base64
            with open(reference_image, 'rb') as f:
                img_data = base64.b64encode(f.read()).decode()
                ext = Path(reference_image).suffix.lower().replace('.', '')
                payload["image"] = f"data:image/{ext};base64,{img_data}"

    print(f"正在生成图片: {prompt[:50]}...")
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        print(f"错误: {response.status_code}")
        print(response.text)
        sys.exit(1)

    result = response.json()

    if 'data' not in result or len(result['data']) == 0:
        print("错误: 未生成图片")
        print(result)
        sys.exit(1)

    image_url = result['data'][0]['url']
    print(f"✅ 图片生成成功: {image_url}")

    # 如果指定了输出路径，下载图片
    if output_path:
        print(f"正在下载图片到: {output_path}")
        img_response = requests.get(image_url)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(img_response.content)
        print(f"✅ 图片已保存")
        return output_path

    return image_url

def main():
    parser = argparse.ArgumentParser(description='生成首尾帧图片')
    parser.add_argument('--prompt', '-p', required=True, help='图片描述')
    parser.add_argument('--reference', '-r', help='参考图片URL或路径')
    parser.add_argument('--size', '-s', default='2560x1440',
                        help='图片尺寸，如2560x1440（16:9）、1440x2560（9:16）、2K、4K')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--first-frame', action='store_true', help='生成首帧')
    parser.add_argument('--last-frame', action='store_true', help='生成尾帧')
    parser.add_argument('--output-dir', default='./keyframes', help='输出目录')

    args = parser.parse_args()

    # 如果指定了首帧或尾帧，生成对应的图片
    if args.first_frame or args.last_frame:
        os.makedirs(args.output_dir, exist_ok=True)

        if args.first_frame:
            first_prompt = f"视频首帧：{args.prompt}，清晰的产品展示或场景开场"
            first_output = os.path.join(args.output_dir, 'first_frame.jpg')
            generate_image(first_prompt, args.reference, args.size, first_output)

        if args.last_frame:
            last_prompt = f"视频尾帧：{args.prompt}，引导关注或行动号召的画面"
            last_output = os.path.join(args.output_dir, 'last_frame.jpg')
            generate_image(last_prompt, args.reference, args.size, last_output)
    else:
        # 单张图片生成
        generate_image(args.prompt, args.reference, args.size, args.output)

if __name__ == '__main__':
    main()
