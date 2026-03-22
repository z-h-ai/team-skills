#!/bin/bash
# 视频拼接脚本 - 使用FFmpeg拼接多个视频片段
# 用法: ./concat_videos.sh <clips_dir> [output.mp4]

set -e

CLIPS_DIR="${1:-.}"
OUTPUT="${2:-output.mp4}"

# 如果OUTPUT是相对路径且不包含目录分隔符，则保存到项目根目录
if [[ "$OUTPUT" != /* ]] && [[ "$OUTPUT" != */* ]]; then
    # 查找项目根目录（包含config.js的目录）
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_ROOT="$SCRIPT_DIR"
    while [[ "$PROJECT_ROOT" != "/" ]]; do
        if [[ -f "$PROJECT_ROOT/config.js" ]]; then
            break
        fi
        PROJECT_ROOT="$(dirname "$PROJECT_ROOT")"
    done

    # 如果找到项目根目录，使用它；否则使用当前目录
    if [[ -f "$PROJECT_ROOT/config.js" ]]; then
        OUTPUT="$PROJECT_ROOT/$OUTPUT"
    fi
fi

# 检查FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "错误: 请先安装FFmpeg"
    echo "  macOS: brew install ffmpeg"
    echo "  Ubuntu: sudo apt install ffmpeg"
    exit 1
fi

# 检查目录
if [ ! -d "$CLIPS_DIR" ]; then
    echo "错误: 目录不存在: $CLIPS_DIR"
    exit 1
fi

# 检查filelist.txt
FILELIST="$CLIPS_DIR/filelist.txt"
if [ ! -f "$FILELIST" ]; then
    echo "filelist.txt不存在，自动生成..."

    # 查找所有clip_*.mp4文件
    cd "$CLIPS_DIR"
    ls clip_*.mp4 2>/dev/null | sort | while read f; do
        echo "file '$f'"
    done > filelist.txt
    cd - > /dev/null

    if [ ! -s "$FILELIST" ]; then
        echo "错误: 没有找到clip_*.mp4文件"
        exit 1
    fi
fi

# 显示要拼接的文件
echo "要拼接的视频片段:"
cat "$FILELIST" | sed 's/^/  /'
echo

# 拼接视频
echo "正在拼接视频..."
cd "$CLIPS_DIR"
ffmpeg -f concat -safe 0 -i filelist.txt -c copy "$(basename "$OUTPUT")" -y
cd - > /dev/null

# 如果输出路径不在clips目录，移动文件
if [[ "$OUTPUT" != "$CLIPS_DIR"* ]]; then
    mv "$CLIPS_DIR/$(basename "$OUTPUT")" "$OUTPUT"
fi

# 检查输出
if [ -f "$OUTPUT" ]; then
    SIZE=$(du -h "$OUTPUT" | cut -f1)
    DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$OUTPUT" 2>/dev/null | cut -d. -f1)

    echo
    echo "拼接完成!"
    echo "  输出文件: $OUTPUT"
    echo "  文件大小: $SIZE"
    echo "  视频时长: ${DURATION}秒"
else
    echo "错误: 拼接失败"
    exit 1
fi
