#!/usr/bin/env python3
"""
音频转录脚本 - 使用火山引擎语音识别极速版API提取视频对白
用法: python transcribe_audio.py <video_path> [--output output.json]
"""

import os
import sys
import json
import uuid
import argparse
import subprocess
import tempfile
import base64
from pathlib import Path


def load_config():
    """从项目根目录的config.js读取配置"""
    current_dir = Path(__file__).resolve().parent

    # 向上查找config.js
    for parent in [current_dir] + list(current_dir.parents):
        config_path = parent / "config.js"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                content = f.read()

                # 提取SPEECH_APP_KEY
                app_key = None
                access_key = None

                for line in content.split("\n"):
                    if "SPEECH_APP_KEY:" in line:
                        app_key = os.getenv("SPEECH_APP_KEY")
                        if not app_key and "'" in line:
                            parts = line.split("'")
                            if len(parts) >= 2:
                                default_key = parts[-2]
                                if default_key and default_key != "YOUR_SPEECH_APP_KEY":
                                    app_key = default_key

                    if "SPEECH_ACCESS_KEY:" in line:
                        access_key = os.getenv("SPEECH_ACCESS_KEY")
                        if not access_key and "'" in line:
                            parts = line.split("'")
                            if len(parts) >= 2:
                                default_key = parts[-2]
                                if default_key and default_key != "YOUR_SPEECH_ACCESS_KEY":
                                    access_key = default_key

                if app_key and access_key:
                    return app_key, access_key
            break

    # 如果config.js中没找到，尝试环境变量
    return os.getenv("SPEECH_APP_KEY"), os.getenv("SPEECH_ACCESS_KEY")


def extract_audio(video_path: str, output_path: str) -> bool:
    """从视频中提取音频为MP3格式"""
    try:
        cmd = [
            'ffmpeg', '-i', video_path,
            '-vn',  # 不包含视频
            '-acodec', 'libmp3lame',  # MP3编码
            '-ar', '16000',  # 采样率16kHz
            '-ac', '1',  # 单声道
            '-y',  # 覆盖输出文件
            output_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"提取音频失败: {e}")
        return False


def file_to_base64(file_path: str) -> str:
    """将文件转换为base64编码"""
    with open(file_path, 'rb') as f:
        file_data = f.read()
        base64_data = base64.b64encode(file_data).decode('utf-8')
    return base64_data


def transcribe_audio_flash(audio_path: str, app_key: str, access_key: str):
    """使用极速版API转录音频（支持base64直接上传）"""
    import requests

    # 检查文件大小（极速版限制100MB）
    file_size = os.path.getsize(audio_path) / (1024 * 1024)
    if file_size > 100:
        raise Exception(f"音频文件过大 ({file_size:.1f}MB)，极速版最大支持100MB")

    print(f"正在转换音频为base64编码...")
    base64_data = file_to_base64(audio_path)

    task_id = str(uuid.uuid4())
    url = "https://openspeech.bytedance.com/api/v3/auc/bigmodel/recognize/flash"

    headers = {
        "X-Api-App-Key": app_key,
        "X-Api-Access-Key": access_key,
        "X-Api-Resource-Id": "volc.bigasr.auc_turbo",  # 极速版资源ID
        "X-Api-Request-Id": task_id,
        "X-Api-Sequence": "-1",
        "Content-Type": "application/json"
    }

    payload = {
        "user": {
            "uid": app_key
        },
        "audio": {
            "data": base64_data  # 使用base64编码的音频数据
        },
        "request": {
            "model_name": "bigmodel",
            "enable_itn": True,  # 文本规范化
            "enable_punc": True,  # 启用标点
            "enable_ddc": True,  # 启用顺滑
            "show_utterances": True  # 返回分句信息和时间戳
        }
    }

    print("正在提交转录任务（极速版，无需等待）...")
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        status_code = response.headers.get("X-Api-Status-Code")
        if status_code == "20000000":
            print("✅ 转录完成")
            return response.json()
        else:
            error_msg = response.headers.get('X-Api-Message', '未知错误')
            print(f"\n错误详情:")
            print(f"  状态码: {status_code}")
            print(f"  错误信息: {error_msg}")
            if 'X-Tt-Logid' in response.headers:
                print(f"  LogID: {response.headers['X-Tt-Logid']}")
            raise Exception(f"转录失败: {error_msg}")
    else:
        print(f"\n错误详情:")
        print(f"  HTTP状态码: {response.status_code}")
        print(f"  响应头: {dict(response.headers)}")
        try:
            print(f"  响应体: {response.text}")
        except:
            pass
        raise Exception(f"HTTP错误: {response.status_code}，可能需要在火山引擎控制台开通极速版权限 (volc.bigasr.auc_turbo)")


def transcribe_video(video_path: str, output_path: str = None):
    """转录视频音频"""

    # 检查依赖
    try:
        import requests
    except ImportError:
        print("错误: 请先安装依赖: pip install requests")
        sys.exit(1)

    # 加载配置
    app_key, access_key = load_config()
    if not app_key or not access_key:
        print("错误: 未找到SPEECH_APP_KEY或SPEECH_ACCESS_KEY")
        print("请在项目根目录的config.js中配置，或设置环境变量")
        sys.exit(1)

    # 检查视频文件
    if not os.path.exists(video_path):
        print(f"错误: 视频文件不存在: {video_path}")
        sys.exit(1)

    print(f"视频文件: {video_path}")

    # 提取音频
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_audio:
        audio_path = tmp_audio.name

    print("正在提取音频...")
    if not extract_audio(video_path, audio_path):
        print("错误: 音频提取失败")
        sys.exit(1)

    print(f"音频已提取: {audio_path}")

    try:
        # 使用极速版API转录
        result = transcribe_audio_flash(audio_path, app_key, access_key)

        # 输出结果
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\n✅ 转录结果已保存到: {output_path}")
        else:
            print("\n=== 转录结果 ===")
            print(json.dumps(result, ensure_ascii=False, indent=2))

        return result

    except Exception as e:
        print(f"\n❌ 转录失败: {e}")
        sys.exit(1)

    finally:
        # 清理临时文件
        if os.path.exists(audio_path):
            os.remove(audio_path)


def main():
    parser = argparse.ArgumentParser(description="转录视频音频，提取对白（极速版）")
    parser.add_argument("video_path", help="视频文件路径")
    parser.add_argument("--output", "-o", help="输出JSON文件路径")

    args = parser.parse_args()
    transcribe_video(args.video_path, args.output)


if __name__ == "__main__":
    main()
