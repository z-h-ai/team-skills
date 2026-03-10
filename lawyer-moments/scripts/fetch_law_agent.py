"""
Agent 调用的法条获取包装器
优先使用 Agent 的联网能力搜索法条，失败则调用原 fetch_law.py
"""
import sys
import json
from pathlib import Path

# 导入原有的获取函数
sys.path.insert(0, str(Path(__file__).parent))
from fetch_law import get_law_articles, FALLBACK_ARTICLES
import random

def get_articles_from_agent_search(search_results: list[dict]) -> list[str]:
    """从 Agent web_search 结果中提取法条"""
    articles = []
    for result in search_results:
        title = result.get("title", "")
        snippet = result.get("snippet", "")
        # 合并标题和摘要作为法条内容
        if title and snippet:
            article = f"{title} {snippet}"
            articles.append(article)
        elif title:
            articles.append(title)
    return articles

def main():
    """
    使用方式：
    1. Agent 先调用 web_search 搜索法条
    2. 将结果 JSON 通过 stdin 传入此脚本
    3. 脚本解析并返回法条列表
    
    如果没有 stdin 输入，则调用原 fetch_law.py 的逻辑
    """
    # 检查是否有 stdin 输入
    if not sys.stdin.isatty():
        try:
            input_data = sys.stdin.read()
            search_results = json.loads(input_data)
            articles = get_articles_from_agent_search(search_results)
            if articles:
                print(json.dumps(articles[:3], ensure_ascii=False))
                return
        except Exception as e:
            print(f"解析 Agent 搜索结果失败: {e}", file=sys.stderr)
    
    # 降级：使用原有逻辑
    articles = get_law_articles(3)
    print(json.dumps(articles, ensure_ascii=False))

if __name__ == "__main__":
    main()
