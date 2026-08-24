from pathlib import Path
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parent
URL = f"file:///{ROOT.as_posix()}/index.html"


def run():
    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # ---- 移动端 full-page（先滚动到底再回顶，确保图片/入场动画触发） ----
        page = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1)
        page.on("console", lambda msg: errors.append(f"console:{msg.type}:{msg.text}") if msg.type == "error" else None)
        page.on("pageerror", lambda exc: errors.append(f"pageerror:{exc}"))
        page.goto(URL)
        page.wait_for_load_state("networkidle")

        # P0 命门校验：任何 .reveal 不得是 opacity:0（整页截图不空白）
        hidden = page.evaluate("()=>[...document.querySelectorAll('.reveal')].filter(el=>getComputedStyle(el).opacity==='0').length")
        assert hidden == 0, f"仍有 {hidden} 个 .reveal 为 opacity:0，会导致截图空白"

        # ---- 叙事改版断言：东陂的天空 / 红色南粤 · 冯达飞 / 生平时间线 ----
        assert "东陂的天空" in page.title(), "<title> 未改为《东陂的天空》"
        assert page.locator("#timeline").count() == 1, "冯达飞生平时间线缺失"
        assert page.locator("#timeline .tl-item").count() >= 4, "时间线条目不足 4 项（应为 1901/1924/1932/1942）"
        assert "东陂的根" in page.locator("#journey .stage h3").nth(0).inner_text(), "航段01未落到‘东陂的根’"
        assert "记住冯达飞" in page.locator(".final h2").inner_text(), "结尾未点题‘记住冯达飞 / 记住红色南粤’"
        assert "东陂的天空" in page.locator(".manifesto-old").inner_text(), "序言旧标题副线未标注‘东陂的天空’"
        assert "驾驶缴获的飞机" in page.locator("#journey .stage").nth(2).inner_text(), "航段03未落到‘驾驶缴获的飞机首飞中央苏区’"
        assert "空军英烈墙" in page.locator("#timeline").inner_text(), "生平时间线未含1942新疆牺牲/空军英烈墙"
        assert "基于公开史实的艺术化演绎" in page.locator(".dhu-note").text_content(), "数字人note未保留‘基于公开史实的艺术化演绎’"

        # 全页截图（滚动到底再回顶，内容应全部可见）
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(400)
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(350)
        page.screenshot(path=str(ROOT / "preview-mobile.png"), full_page=True)

        # ---- 既有交互断言 ----
        page.locator("#startJourney").click()
        page.locator("#lionButton").click()
        assert page.locator("#lionStatus").inner_text() == "已经醒来", "醒狮状态未变‘已经醒来’"
        # 02 扎染：捆扎→浸染→解开
        page.locator("#paintPad").scroll_into_view_if_needed()
        page.locator(".bind-opt").nth(1).click()
        page.locator(".dye-opt").nth(0).click()
        page.locator("#dyeSoak").click()
        page.locator("#dyeUntie").click()
        assert "展开了" in page.locator("#paintPad .paint-copy").inner_text(), "扎染文案未含‘展开了’"
        # 04 信件淡入小窗
        page.locator("#letterOpen").scroll_into_view_if_needed()
        page.locator("#letterOpen").click()
        assert page.locator("#letterModal").evaluate("(el) => el.classList.contains('open')"), "信件小窗未打开"
        assert "黄埔军校第一期" in page.locator("#letterModal .letter-body").inner_text(), "信件未含黄埔军校史实"
        assert "百色起义" in page.locator("#letterModal .letter-body").inner_text(), "信件未含广州/百色起义史实"
        assert "飞行教官" in page.locator("#letterModal .letter-body").inner_text(), "信件未含红军/人民军队飞行教官史实"
        assert "上饶集中营" in page.locator("#letterModal .letter-body").inner_text(), "信件未含1942上饶集中营牺牲史实"
        assert "空军英烈墙" in page.locator("#letterModal .letter-body").inner_text(), "信件未含空军英烈墙"
        assert "驾驶缴获的飞机" in page.locator("#letterModal .letter-body").inner_text(), "信件未含‘驾驶缴获飞机首飞中央苏区’"
        page.locator("#letterClose").click()
        assert not page.locator("#letterModal").evaluate("(el) => el.classList.contains('open')"), "信件小窗未关闭"
        page.locator("#rocketButton").click()
        # 04 数字人视频弹窗
        page.locator("#dhuPlay").scroll_into_view_if_needed()
        page.locator("#dhuPlay").click()
        assert page.locator("#dhuModal").evaluate("(el) => el.classList.contains('open')"), "数字人弹窗未打开"
        page.locator("#dhuClose").click()
        assert not page.locator("#dhuModal").evaluate("(el) => el.classList.contains('open')"), "数字人弹窗未关闭"

        # ---- 新增：纸飞机 UGC / 队徽 / AI 标注 ----
        page.locator("#wish").scroll_into_view_if_needed()
        page.locator("#wishInput").fill("愿你飞得又高又远。")
        page.locator("#makePlane").click()
        assert page.locator("#cardStage").evaluate("(el) => el.classList.contains('show')"), "纸飞机卡片未生成"
        assert page.locator("#cardActions").is_visible(), "卡片操作按钮不可见"
        # 队徽出现于 topbar + final
        assert page.locator("#brandLogo").count() == 1, "topbar 队徽缺失"
        assert page.locator("img[src*='team_logo']").count() >= 2, "队徽未在结尾出现"
        # AI 标注行
        ai = page.locator(".ai-note").inner_text()
        assert "AI 辅助生成" in ai, "AI 生成标注缺失"
        page.locator("#shareButton").click()

        # ---- 桌面端 full-page ----
        page.set_viewport_size({"width": 1440, "height": 900})
        page.reload()
        page.wait_for_load_state("networkidle")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(400)
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(350)
        page.screenshot(path=str(ROOT / "preview-desktop.png"), full_page=True)

        browser.close()

    if errors:
        raise RuntimeError("\n".join(errors))


if __name__ == "__main__":
    run()
