import asyncio
import random
import datetime
import logging
import csv
from pathlib import Path
from playwright.async_api import async_playwright

BASE_URL = "https://www.imdb.com"
TOP_URL = "https://www.imdb.com/chart/top/"

CONCURRENCY = 3  # ⭐ 降低并发（关键）

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ✅ 获取链接
async def get_links(page):
    await page.goto(TOP_URL)
    await page.wait_for_selector("li.ipc-metadata-list-summary-item")

    items = page.locator("li.ipc-metadata-list-summary-item")
    count = await items.count()

    links = []
    for i in range(count):
        href = await items.nth(i).locator("a").first.get_attribute("href")
        links.append((i + 1, BASE_URL + href.split("?")[0]))

    return links


# ✅ 稳定获取 rating（核心优化）
async def safe_get_rating(page):
    for _ in range(3):
        try:
            locator = page.locator(
                "[data-testid='hero-rating-bar__aggregate-rating__score'] span"
            ).first

            if await locator.count() > 0:
                text = await locator.text_content()
                if text:
                    return text.strip()

        except:
            pass

        await asyncio.sleep(1)

    return ""


# ✅ 单任务（稳定版）
async def parse_movie(context, sem, rank, url):
    async with sem:
        page = await context.new_page()

        try:
            await page.goto(url, timeout=60000)

            # ⭐ 等标题
            await page.wait_for_selector("h1", timeout=15000)

            # ⭐ 关键：再等一会（让JS跑完）
            await asyncio.sleep(random.uniform(1, 2))

            title = await page.locator("h1").inner_text()

            rating = await safe_get_rating(page)

            # year
            try:
                year = await page.locator("a[href*='releaseinfo']").first.inner_text()
            except:
                year = ""

            # runtime
            try:
                runtime = await page.locator(
                    "li[data-testid='title-techspec_runtime'] span"
                ).last.inner_text()
            except:
                runtime = ""

            logger.info(f"[{rank}] ✅ {title}")

            return {
                "ranking": rank,
                "title": title,
                "year": year,
                "runtime": runtime,
                "rating": rating
            }

        except Exception as e:
            logger.warning(f"[{rank}] ❌ 失败: {url}")
            return None

        finally:
            await page.close()

            # ⭐ 每个请求后休息（关键）
            await asyncio.sleep(random.uniform(1.5, 3))


# ✅ 主流程
async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            locale="en-US"
        )

        page = await context.new_page()

        links = await get_links(page)
        random.shuffle(links)

        sem = asyncio.Semaphore(CONCURRENCY)

        tasks = [
            parse_movie(context, sem, rank, url)
            for rank, url in links
        ]

        results = await asyncio.gather(*tasks)

        await browser.close()

        results = [r for r in results if r]
        results.sort(key=lambda x: x["ranking"])

        logger.info(f"成功 {len(results)} / {len(links)}")

        return results


# ✅ CSV
def write_csv(data, file_name):
    Path("csv_data").mkdir(exist_ok=True)

    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["ranking", "title", "year", "runtime", "rating"]
        )
        writer.writeheader()
        writer.writerows(data)


# ✅ 入口
if __name__ == "__main__":
    file_name = f"csv_data/imdb_top250_{datetime.date.today()}.csv"

    Path(file_name).unlink(missing_ok=True)

    data = asyncio.run(run())

    write_csv(data, file_name)