"""
用 Playwright 从全国人大法律法规数据库爬取劳动法相关法条
返回 3 条法条文本列表
"""
import asyncio
import json
import random
from playwright.async_api import async_playwright

KEYWORDS = ["劳动合同", "工资报酬", "解除劳动合同", "经济补偿", "工作时间",
            "休息休假", "社会保险", "劳动保护", "违约金", "竞业限制"]

# 内置备用法条（当爬取失败时使用）
FALLBACK_ARTICLES = [
    "《劳动合同法》第47条：经济补偿按劳动者在本单位工作的年限，每满一年支付一个月工资的标准向劳动者支付。六个月以上不满一年的，按一年计算；不满六个月的，向劳动者支付半个月工资的经济补偿。",
    "《劳动法》第44条：安排劳动者延长工作时间的，支付不低于工资百分之一百五十的工资报酬；休息日安排劳动者工作又不能安排补休的，支付不低于工资百分之二百；法定休假日安排劳动者工作的，支付不低于工资百分之三百的工资报酬。",
    "《劳动合同法》第38条：用人单位未及时足额支付劳动报酬的，或未依法为劳动者缴纳社会保险费的，劳动者可以解除劳动合同并要求经济补偿。",
    "《劳动合同法》第14条：劳动者在该用人单位连续工作满十年的，或连续订立二次固定期限劳动合同后再续签的，劳动者提出或者同意续订劳动合同的，应当订立无固定期限劳动合同。",
    "《劳动法》第36条：国家实行劳动者每日工作时间不超过八小时、平均每周工作时间不超过四十四小时的工时制度。",
    "《劳动合同法》第82条：用人单位自用工之日起超过一个月不满一年未与劳动者订立书面劳动合同的，应当向劳动者每月支付二倍的工资。",
    "《劳动法》第50条：工资应当以货币形式按月支付给劳动者本人，不得克扣或者无故拖欠劳动者的工资。",
    "《劳动合同法》第23条：用人单位与劳动者可以在劳动合同中约定保守用人单位的商业秘密和与知识产权相关的保密事项。竞业限制期限不得超过二年。",
    "《工伤保险条例》第14条：职工在工作时间和工作场所内，因工作原因受到事故伤害的，应当认定为工伤。",
    "《劳动合同法》第87条：用人单位违反本法规定解除或者终止劳动合同的，应当依照本法第47条规定的经济补偿标准的二倍向劳动者支付赔偿金。",
]

async def fetch_articles_playwright(keyword: str) -> list[str]:
    """用 Playwright 爬取法条，返回法条文本列表"""
    articles = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
        )
        page = await context.new_page()
        
        law_responses = []
        
        async def on_response(response):
            if "law-search/search/list" in response.url and response.status == 200:
                try:
                    data = await response.json()
                    law_responses.append(data)
                except Exception:
                    pass
        
        page.on("response", on_response)
        
        try:
            await page.goto("https://flk.npc.gov.cn", wait_until="domcontentloaded", timeout=20000)
            await page.wait_for_timeout(2000)
            
            # 填写搜索框并搜索
            await page.fill('input[placeholder="请输入"]', keyword)
            await page.wait_for_timeout(500)
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(4000)
            
        except Exception as e:
            print(f"  Playwright 页面操作失败: {e}")
        finally:
            await browser.close()
        
        # 解析响应
        for resp_data in law_responses:
            # 尝试各种可能的数据结构
            items = (
                resp_data.get("data", {}).get("list", []) or
                resp_data.get("data", []) or
                resp_data.get("result", {}).get("data", []) or
                []
            )
            for item in items[:5]:
                title = item.get("title", "")
                if title:
                    articles.append(title)
    
    return articles


def get_law_articles(count: int = 3) -> list[str]:
    """
    获取 count 条劳动法相关法条。
    优先用 Playwright 爬取，失败则使用内置备用法条。
    """
    keyword = random.choice(KEYWORDS)
    print(f"  正在爬取法条，关键词: {keyword}")
    
    try:
        articles = asyncio.run(fetch_articles_playwright(keyword))
        if articles:
            print(f"  爬取成功，获得 {len(articles)} 条结果")
            # 随机取 count 条
            selected = random.sample(articles, min(count, len(articles)))
            return selected
        else:
            print("  爬取返回空结果，使用内置备用法条")
    except Exception as e:
        print(f"  爬取异常: {e}，使用内置备用法条")
    
    # 降级：随机从内置法条中取 count 条
    return random.sample(FALLBACK_ARTICLES, count)


if __name__ == "__main__":
    print("测试法条爬取...")
    articles = get_law_articles(3)
    print(f"\n获取到 {len(articles)} 条法条:")
    for i, a in enumerate(articles, 1):
        print(f"  {i}. {a}")
