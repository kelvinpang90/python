from playwright.sync_api import sync_playwright
from undetected_playwright import stealth_sync
import time
import json
import random
import logging
import os
from twocaptcha import TwoCaptcha
import requests
import io
import pdfplumber

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_URL = (
    "https://scholar.google.com/scholar?hl=zh-CN&as_sdt=0,5"
    "&q=Psychological+capital+Innovative+behavior+motivation+knowledge+sharing"
)

API_KEY = "fca5f5db05b2b2c8cbf7b8569c258bbf"  # 请替换为您的2Captcha API密钥

# 随机User-Agent列表
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
]

# 固定User-Agent以保持指纹一致性
FIXED_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def parse_results(page, browser, page_index, context_params):
    """提取当前页面的文献条目"""
    items = []
    try:
        # 等待页面加载并确保文献条目已经渲染出来
        page.wait_for_selector("div.gs_r.gs_or.gs_scl", timeout=2000)  # 增加等待时间至10秒
    except:
        logging.warning("    → Selector not found, skipping page")
        page.screenshot(path=f"no_selector_{page_index}.png")
        content = page.content()
        logging.info(f"页面内容前1000字符: {content[:1000]}")
        return items

    # 每条论文
    results = page.query_selector_all("div.gs_r.gs_or.gs_scl")
    for r in results:
        title_el = r.query_selector("h3.gs_rt")
        title = title_el.inner_text() if title_el else ""

        # 获取论文链接
        link = ""
        if title_el:
            a = title_el.query_selector("a")
            link = a.get_attribute("href") if a else ""

        # 作者 + 出版信息
        info_el = r.query_selector("div.gs_a")
        info = info_el.inner_text() if info_el else ""

        # 摘要（从Google页面）
        abs_el = r.query_selector("div.gs_rs")
        abstract = abs_el.inner_text() if abs_el else ""

        # 尝试进入论文页面获取完整内容
        full_content = ""
        if link:
            try:
                if link.endswith('.pdf'):
                    # 处理PDF
                    response = requests.get(link, timeout=10)
                    pdf_file = io.BytesIO(response.content)
                    with pdfplumber.open(pdf_file) as pdf:
                        text = ""
                        for page in pdf.pages:
                            page_text = page.extract_text()
                            if page_text:
                                text += page_text
                    full_content = text[:20000]
                else:
                    # 正常页面
                    new_context = browser.new_context(**context_params)
                    new_page = new_context.new_page()
                    stealth_sync(new_page)
                    new_page.goto(link, timeout=20000)
                    time.sleep(1)  # 等待加载
                    # 检查是否遇到Cloudflare验证
                    for attempt in range(3):
                        page_content = new_page.evaluate("document.body.innerText").lower()
                        if "performing security verification" in page_content or "cloudflare" in page_content:
                            logging.warning(f"    → 检测到Cloudflare验证，等待并重试 ({attempt + 1}/3)")
                            time.sleep(10)
                            new_page.reload()
                            time.sleep(5)
                        else:
                            break
                    # 提取页面摘要内容
                    abstract_element = new_page.query_selector('[class*="abstract"]') or new_page.query_selector('[id*="abstract"]') or new_page.query_selector('div.abstract') or new_page.query_selector('section.abstract')
                    if abstract_element:
                        full_content = abstract_element.inner_text()
                    else:
                        # 如果找不到摘要元素，提取正文前2000字符
                        body_text = new_page.evaluate("document.body.innerText")
                        full_content = body_text[:20000]
                    new_page.close()
                    new_context.close()
            except Exception as e:
                logging.warning(f"    → 获取 {link} 内容失败: {e}")
                full_content = abstract  # 回退到预览摘要

        # 引用次数
        cite_el = r.query_selector("div.gs_fl a:nth-child(3)")
        cited_by = cite_el.inner_text() if cite_el else ""

        items.append({
            "title": title,
            "link": link,
            "info": info,
            "abstract": abstract,
            "full_content": full_content,
            "cited_by": cited_by,
        })
    return items


def main():
    all_data = []
    if os.path.exists("json_data/scholar_results.json"):
        with open("json_data/scholar_results.json", "r", encoding="utf-8") as f:
            try:
                all_data = json.load(f)
            except json.JSONDecodeError:
                all_data = []
    with sync_playwright() as p:
        # 定义浏览器profile目录和storage state文件
        user_data_dir = "browser_profile"
        storage_state_file = "storage_state.json"
        
        # 定义context参数
        context_params = {
            "user_agent": FIXED_USER_AGENT,
            "locale": "zh-CN",
            "timezone_id": "Asia/Shanghai",
            "geolocation": {"latitude": 39.9042, "longitude": 116.4074},
            "permissions": ["geolocation"],
            "viewport": {"width": 1280, "height": 720},
            "device_scale_factor": 1,
            "is_mobile": False,
            "has_touch": False,
            "color_scheme": "light",
            "reduced_motion": "no-preference",
        }
        
        # 使用launch_persistent_context创建持久化上下文
        context = p.chromium.launch_persistent_context(user_data_dir=user_data_dir, headless=False, **context_params)
        page = context.new_page()
        stealth_sync(page)  # 应用隐身模式

        for page_index in range(0, 1):
            start = page_index * 10
            url = f"{BASE_URL}&start={start}"

            logging.info(f"📄 抓取第 {page_index + 1} 页： {url}")
            page.goto(url)
            # 模拟人类行为：随机移动鼠标
            page.mouse.move(random.randint(0, 1280), random.randint(0, 720))
            time.sleep(random.uniform(0.5, 1.5))
            page.mouse.move(random.randint(0, 1280), random.randint(0, 720))
            time.sleep(random.uniform(0.5, 1.5))
            time.sleep(3)  # 额外等待页面加载

            # 等待页面加载完成
            page.wait_for_load_state('networkidle', timeout=30000)  # 等待页面所有请求完成

            # 模拟更多人类行为
            for _ in range(random.randint(3, 5)):
                page.mouse.move(random.randint(0, 1280), random.randint(0, 720))
                time.sleep(random.uniform(0.5, 1.5))
            # 模拟键盘行为
            page.keyboard.press("Tab")
            time.sleep(random.uniform(0.5, 1.0))
            page.keyboard.press("Tab")
            time.sleep(random.uniform(0.5, 1.0))
            # 随机输入一些字符然后删除
            if random.random() > 0.5:
                page.keyboard.type("test")
                time.sleep(random.uniform(0.5, 1.0))
                for _ in range(4):
                    page.keyboard.press("Backspace")
                    time.sleep(random.uniform(0.1, 0.3))
            page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2);")
            time.sleep(random.uniform(1, 2))
            page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(1, 2))
            page.evaluate("window.scrollTo(0, 0);")
            time.sleep(random.uniform(1, 2))

            # 检查是否出现验证码 / 人机验证
            content = page.evaluate("document.body.innerText").lower()
            if "请验证您是" in content or "verify" in content or "captcha" in content or "异常流量" in content:
                logging.warning("❌ 检测到验证码或阻断，正在尝试使用2Captcha解决...")
                logging.info(f"当前URL: {page.url}")
                logging.info("页面内容片段:")
                logging.info(content[:1000])  # 前1000字符
                page.screenshot(path=f"captcha_page_{page_index}.png")
                if "异常流量" in content:
                    logging.warning("检测到Google阻断页面，停止抓取")
                    break
                try:
                    # 查找reCAPTCHA的sitekey
                    sitekey_element = page.query_selector('[data-sitekey]')
                    if not sitekey_element:
                        # 尝试在reCAPTCHA iframe中查找
                        recaptcha_iframe = page.query_selector('iframe[src*="recaptcha"]')
                        if recaptcha_iframe:
                            frame = recaptcha_iframe.content_frame
                            sitekey_element = frame.query_selector('[data-sitekey]')
                    if sitekey_element:
                        sitekey = sitekey_element.get_attribute('data-sitekey')
                        current_url = page.url
                        solver = TwoCaptcha(API_KEY)
                        result = solver.recaptcha(sitekey=sitekey, url=current_url)
                        token = result['code']
                        # 设置g-recaptcha-response
                        page.evaluate(f"document.getElementById('g-recaptcha-response').value = '{token}';")
                        # 查找并点击提交按钮（如果有）
                        submit_button = page.query_selector('input[type="submit"]') or page.query_selector('button[type="submit"]') or page.query_selector('.recaptcha-submit')
                        if submit_button:
                            submit_button.click()
                        else:
                            # 如果没有明确的提交按钮，可能需要刷新或等待
                            page.reload()
                        time.sleep(5)  # 等待处理
                        # 重新检查是否还有验证码
                        if "请验证您是" in page.evaluate("document.body.innerText").lower() or "verify" in page.evaluate("document.body.innerText").lower() or "captcha" in page.evaluate("document.body.innerText").lower() or "异常流量" in page.evaluate("document.body.innerText").lower():
                            logging.warning("❌ 验证码解决失败")
                            break
                        else:
                            logging.info("✅ 验证码解决成功，继续抓取")
                            continue
                    else:
                        logging.warning("❌ 未找到reCAPTCHA sitekey")
                        break
                except Exception as e:
                    logging.warning(f"❌ 解决验证码时出错: {e}")
                    break

            # 滚动页面，确保加载更多的内容
            page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # 等待内容加载

            items = parse_results(page, context.browser, page_index, context_params)
            logging.info(f"    → 当前页提取到 {len(items)} 条")
            all_data.extend(items)

            time.sleep(random.randint(10, 20))  # 随机等待10到20秒以避免检测

        # 保存storage state
        context.storage_state(path=storage_state_file)
        context.close()

    # 保存结果
    with open("json_data/scholar_results.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    logging.info("✅ 完成，已保存到 scholar_results.json")


if __name__ == "__main__":
    main()