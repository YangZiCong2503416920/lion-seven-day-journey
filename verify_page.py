from pathlib import Path
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parent
URL = f"file:///{ROOT.as_posix()}/index.html"

# 全页任何可见/隐藏叙事文本都不得出现的词条（红色叙事口径：已 Cut 词 + 史实禁用词）
FORBIDDEN = ["醒狮", "扎染", "非遗", "科创", "参加北伐", "南昌起义", "新疆"]
# 仅允许出现在【学校章节 #school】与【纸飞机 UGC #wish】的航天精神风貌词，
# 不得进入冯达飞的历史叙事（#manifesto / #journey / #timeline / .letter-body / .final）
SCOPE_ONLY = ["水火箭", "纸飞机"]


def _narrative_text(page):
    """历史叙事容器（不含学校章节与 UGC），供‘水火箭/纸飞机仅限学校+UGC’检查。"""
    parts = [
        page.locator("#manifesto").inner_text(),
        page.locator("#journey").inner_text(),
        page.locator("#timeline").inner_text(),
        page.locator(".letter-body").text_content(),
        page.locator(".final").inner_text(),
    ]
    return "\n".join(parts)


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

        # ---- 标题 / meta / 主题 ----
        assert "飞出去" in page.title(), "<title> 未改订为《飞出去》"
        assert "红色南粤" in page.title(), "<title> 未含‘红色南粤’"
        assert "连州市实验小学" in page.title(), "<title> 未含‘连州市实验小学’（学校层）"
        desc = page.locator('meta[name=description]').get_attribute("content")
        assert desc and "飞出去" in desc and "连州市实验小学" in desc, "meta description 未同步"

        # ---- 已 Cut 词 / 史实禁用词：全页均不得出现 ----
        full_visible = page.locator("body").inner_text()
        letter_text = page.locator(".letter-body").text_content()
        all_text = full_visible + "\n" + letter_text
        for w in FORBIDDEN:
            assert w not in all_text, f"页面仍出现已 Cut / 禁用词条：{w}"

        # ---- 航天精神风貌（水火箭/纸飞机）仅限学校章节与 UGC，不得进历史叙事 ----
        narrative = _narrative_text(page)
        for w in SCOPE_ONLY:
            assert w not in narrative, f"历史叙事出现【{w}】：应只出现在学校章节与纸飞机UGC"

        # ---- 冯达飞历史叙事：正向史实断言 ----
        journey = page.locator("#journey").inner_text()
        assert "黄埔军校第一期" in journey, "航程未落‘黄埔军校第一期’"
        assert "东征" in journey, "航程未落‘1925 东征（讨伐陈炯明）’"
        assert "广州起义" in journey, "航程未落‘1927 广州起义’"
        assert "百色起义" in journey, "航程未落‘1929 百色起义’"
        assert "驾驶" in journey and "缴获" in journey, "航程未落‘驾驶缴获飞机首飞中央苏区’"
        assert "红色根据地" in journey, "航程未落‘首次由己方飞行员驾机飞回红色根据地’"
        assert "上饶集中营" in journey, "航程未落‘1942 上饶集中营牺牲’"
        assert "空军英烈墙" in journey, "航程未落‘空军英烈墙’"
        assert "飞行教官" in journey, "航程未落‘空军首位飞行教官’"
        assert "人民军队航空先驱" in journey, "航程未落‘人民军队航空先驱’"

        # ---- 红色书信（史实总纲） ----
        assert "黄埔军校第一期" in letter_text
        assert "同年冬加入中国共产党" in letter_text
        assert "东征" in letter_text
        assert "随后赴苏联学习航空；1927" in letter_text, "时序有误：赴苏应早于1927归国/起义"
        assert "广州起义" in letter_text
        assert "百色起义" in letter_text
        assert "人民军队航空先驱" in letter_text
        assert "飞行教官" in letter_text
        assert "驾驶缴获的飞机" in letter_text
        assert "上饶集中营" in letter_text
        assert "空军英烈墙" in letter_text
        assert "参加北伐" not in letter_text, "信件仍写‘参加北伐’（应为东征）"

        # ---- 时间线：完整航线（8 卡） ----
        assert page.locator("#timeline .tl-item").count() == 8, "时间线应为 8 卡（1901/1924/1925/1927/1929/1932/1942/今）"
        tlp = page.locator("#timeline").inner_text()
        for y in ["1901", "1924", "1925", "1927", "1929", "1932", "1942.6"]:
            assert y in tlp, f"时间线缺少 {y}"
        assert "今" in tlp, "时间线缺少‘今’"

        # ---- 承 · 学校（学校层） ----
        assert "连州市实验小学" in page.locator("#school").inner_text(), "学校章节未落学校名"
        assert "航天筑梦" in page.locator("#school").inner_text(), "学校章节未落党建品牌‘航天筑梦’"
        assert "党建筑魂" in page.locator("#school").inner_text(), "学校章节未落党建品牌‘党建筑魂’"

        # ---- 结尾 ----
        assert "记住冯达飞" in page.locator(".final h2").inner_text(), "结尾未点题‘记住冯达飞’"
        assert "学校" in page.locator(".final h2").inner_text(), "结尾未收束到学校"

        # ---- 数字人 + 红色书信（保留并强化） ----
        assert page.locator("#dhuPlay").count() == 1
        assert page.locator("#dhuModal").count() == 1
        assert page.locator("#dhuClose").count() == 1
        assert page.locator("#dhuVideo").count() == 1
        assert page.locator("#letterOpen").count() == 1
        assert page.locator("#letterModal").count() == 1
        assert page.locator("#letterClose").count() == 1
        assert "基于公开史实的艺术化演绎" in page.locator(".dhu-note").text_content(), "数字人note未保留‘基于公开史实的艺术化演绎’"

        # 全页截图（滚动到底再回顶，内容应全部可见）
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(400)
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(350)
        page.screenshot(path=str(ROOT / "preview-mobile.png"), full_page=True)

        # ---- 既有交互断言 ----
        page.locator("#startJourney").click()
        # 数字人视频弹窗
        page.locator("#dhuPlay").scroll_into_view_if_needed()
        page.locator("#dhuPlay").click()
        assert page.locator("#dhuModal").evaluate("(el) => el.classList.contains('open')"), "数字人弹窗未打开"
        page.locator("#dhuClose").click()
        assert not page.locator("#dhuModal").evaluate("(el) => el.classList.contains('open')"), "数字人弹窗未关闭"
        # 红色书信小窗
        page.locator("#letterOpen").scroll_into_view_if_needed()
        page.locator("#letterOpen").click()
        assert page.locator("#letterModal").evaluate("(el) => el.classList.contains('open')"), "信件小窗未打开"
        page.locator("#letterClose").click()
        assert not page.locator("#letterModal").evaluate("(el) => el.classList.contains('open')"), "信件小窗未关闭"
        # 纸飞机 / 红色留言卡 UGC
        page.locator("#wish").scroll_into_view_if_needed()
        page.locator("#wishInput").fill("愿后人记得，有人为这片土地飞过。")
        page.locator("#makeCard").click()
        assert page.locator("#cardStage").evaluate("(el) => el.classList.contains('show')"), "红色留言卡未生成"
        assert page.locator("#cardActions").is_visible(), "卡片操作按钮不可见"
        # 队徽出现于 topbar + final
        assert page.locator("#brandLogo").count() == 1, "topbar 队徽缺失"
        assert page.locator("img[src*='team_logo']").count() >= 2, "队徽未在结尾出现"
        # AI 标注行（非真实影像/录音、不虚构原话）
        ai = page.locator(".ai-note").inner_text()
        assert "非真实历史影像" in ai and "不虚构原话" in ai, "AI 艺术化演绎标注缺失"
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
