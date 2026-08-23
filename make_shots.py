"""生成符合附件4 提交规范的页面截图（JPEG / RGB / 100DPI / <10MB）。

用法：python3 make_shots.py
输出：交互网页/shots/{full_desktop,hero_desktop,full_mobile,hero_mobile}.jpg
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
import io
import os


ROOT = Path(__file__).resolve().parent
URL = f"file:///{ROOT.as_posix()}/index.html"
OUT = ROOT / "shots"
OUT.mkdir(exist_ok=True)


def save_jpeg(png_bytes, name, dpi=100, quality=85):
    im = Image.open(io.BytesIO(png_bytes)).convert("RGB")  # RGB 色彩模式
    path = OUT / name
    im.save(path, "JPEG", quality=quality, dpi=(dpi, dpi), optimize=True)  # 100DPI
    size = os.path.getsize(path) / 1024 / 1024
    print(f"{name:22s} {im.size[0]}x{im.size[1]}  {size:.2f}MB")
    assert size < 10, f"{name} 超 10MB，请降低质量/分辨率"
    return path


def scroll_full(page):
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(420)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(380)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    # 桌面端
    page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
    page.goto(URL)
    page.wait_for_load_state("networkidle")
    scroll_full(page)
    save_jpeg(page.screenshot(full_page=True), "full_desktop.jpg")
    # 勾连“可交互时刻”后再截首屏 hero（互动后内容更饱满）
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(200)
    save_jpeg(page.screenshot(), "hero_desktop.jpg")
    page.close()

    # 移动端
    page = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1)
    page.goto(URL)
    page.wait_for_load_state("networkidle")
    scroll_full(page)
    save_jpeg(page.screenshot(full_page=True), "full_mobile.jpg")
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(200)
    save_jpeg(page.screenshot(), "hero_mobile.jpg")
    page.close()

    browser.close()

print("done ->", OUT)
