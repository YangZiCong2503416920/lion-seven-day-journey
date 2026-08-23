"""生成「互动点亮瞬间」关键帧截图（附件4 提交图集用）。

用法：python3 make_keyframes.py
输出：交互网页/shots/keyframes/*.jpg（JPEG / RGB / 100DPI / <10MB，均已校验）
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
import io, os

ROOT = Path(__file__).resolve().parent
URL = f"file:///{ROOT.as_posix()}/index.html"
OUT = ROOT / "shots" / "keyframes"
OUT.mkdir(parents=True, exist_ok=True)


def save_jpeg(png_bytes, name, dpi=100, quality=85):
    im = Image.open(io.BytesIO(png_bytes)).convert("RGB")
    path = OUT / name
    im.save(path, "JPEG", quality=quality, dpi=(dpi, dpi), optimize=True)
    size = os.path.getsize(path) / 1024 / 1024
    print(f"{name:24s} {im.size[0]}x{im.size[1]}  {size:.2f}MB")
    assert size < 10, f"{name} 超 10MB"
    return path


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    # ---- 移动端：交互点亮瞬间 ----
    page = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1)
    page.goto(URL)
    page.wait_for_load_state("networkidle")

    # 01 首屏 + 点醒醒狮（盖章 + 粒子）
    page.evaluate("window.scrollTo(0,0)")
    page.wait_for_timeout(250)
    page.locator("#lionButton").click()
    page.wait_for_timeout(700)  # 抓住盖章/粒子瞬间（1500ms 内）
    save_jpeg(page.screenshot(), "kf_01_hero_lion.jpg")

    # 02 漆扇展开
    page.locator("#paintPad").scroll_into_view_if_needed()
    page.wait_for_timeout(300)
    page.locator("#paintPad").click()
    page.wait_for_timeout(500)
    save_jpeg(page.screenshot(), "kf_02_paint.jpg")

    # 03 水火箭发射 + 孩子愿望
    page.locator("#rocketZone").scroll_into_view_if_needed()
    page.wait_for_timeout(300)
    page.locator("#rocketButton").click()
    page.wait_for_timeout(1300)  # 打气约900ms后发射；愿望.show持续4200ms
    save_jpeg(page.screenshot(), "kf_03_rocket.jpg")

    # 04 纸飞机祝福卡生成
    page.locator("#wish").scroll_into_view_if_needed()
    page.wait_for_timeout(300)
    page.locator("#wishInput").fill("愿你像纸飞机一样，飞得又高又远。")
    page.locator("#makePlane").click()
    page.wait_for_timeout(600)
    save_jpeg(page.screenshot(), "kf_04_wish_card.jpg")

    page.close()

    # ---- 桌面端：首屏 + 醒狮（补充一张横屏证图） ----
    page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
    page.goto(URL)
    page.wait_for_load_state("networkidle")
    page.evaluate("window.scrollTo(0,0)")
    page.wait_for_timeout(250)
    page.locator("#lionButton").click()
    page.wait_for_timeout(700)
    save_jpeg(page.screenshot(), "kf_05_hero_desktop.jpg")
    page.close()

    browser.close()

print("done ->", OUT)
