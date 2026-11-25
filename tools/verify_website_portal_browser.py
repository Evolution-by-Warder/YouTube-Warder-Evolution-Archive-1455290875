"""Read-only rendering/interaction checks for the public product website."""
import functools
import http.server
import json
import pathlib
import shutil
import threading
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "website-preview"
OUT.mkdir(exist_ok=True)
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT / "docs"))
server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
url = "http://127.0.0.1:%d/index.html" % server.server_port
report = []
try:
    with sync_playwright() as p:
        chrome = shutil.which("google-chrome") or shutil.which("chromium")
        assert chrome, "Installed Chrome/Chromium is required"
        browser = p.chromium.launch(executable_path=chrome, headless=True, args=["--no-sandbox"])
        for name, width, height in (("desktop", 1440, 1000), ("tablet", 768, 1024), ("mobile", 390, 844)):
            context = browser.new_context(viewport={"width": width, "height": height}, locale="en-US",
                                          reduced_motion="reduce", device_scale_factor=1)
            page = context.new_page()
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(url, wait_until="domcontentloaded")
            page.evaluate("document.querySelectorAll('img').forEach(i=>i.loading='eager')")
            page.wait_for_function("Array.from(document.images).every(i=>i.complete && i.naturalWidth>0)", timeout=45000)
            page.evaluate("document.fonts.ready")
            assert page.locator(".product").count() == 5
            assert page.locator("h1").inner_text() == "WARDER\nEVOLUTION"
            assert page.locator("html").get_attribute("lang") == "en"
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), name + " overflow"
            assert page.locator("a[href$='.ipk']").count() == 5
            page.screenshot(path=str(OUT / (name + "-en.png")), full_page=True, animations="disabled")
            if name == "desktop":
                page.screenshot(path=str(OUT / "desktop-hero.png"), animations="disabled")
                page.locator("#products").screenshot(path=str(OUT / "desktop-products.png"), animations="disabled")
            page.locator("button[data-lang='sk']").click()
            assert page.locator("html").get_attribute("lang") == "sk"
            assert page.locator(".hero h2").inner_text() == "Enigma2. V novom svetle."
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), name + " SK overflow"
            page.screenshot(path=str(OUT / (name + "-sk.png")), full_page=True, animations="disabled")
            page.reload(wait_until="domcontentloaded")
            assert page.locator("html").get_attribute("lang") == "sk"
            page.locator("button[data-lang='en']").click()
            assert page.locator("html").get_attribute("lang") == "en"
            product_pages = ("fullhdglass.html","piconhub.html","radio.html","youtube-warder.html","gsu.html")
            checked=[]
            for product_page in product_pages:
                page.goto(url,wait_until="domcontentloaded")
                assert page.locator("html").get_attribute("lang") == "en"
                page.locator(".product .btn.primary[href='"+product_page+"']").click()
                page.wait_for_url("**/"+product_page)
                page.evaluate("document.querySelectorAll('img').forEach(i=>i.loading='eager')")
                gallery=page.locator("#screenshots .screenshot-grid a[data-caption-en][data-caption-sk]")
                expected={"fullhdglass.html":12,"piconhub.html":3,"gsu.html":7,"radio.html":10,"youtube-warder.html":8}
                assert gallery.count()==expected[product_page]
                gallery.first.click()
                dialog=page.locator("dialog.screenshot-dialog")
                assert dialog.is_visible()
                page.wait_for_function("document.querySelector('dialog.screenshot-dialog img').naturalWidth===1920")
                assert dialog.locator("button").first.is_disabled()
                page.keyboard.press("ArrowRight")
                assert dialog.locator(".screenshot-caption").inner_text().startswith("2 /")
                page.keyboard.press("Escape")
                dialog.wait_for(state="detached")
                assert gallery.first.evaluate("a=>document.activeElement===a")
                if name=="desktop":
                    page.locator("#screenshots").screenshot(path=str(OUT/(product_page.removesuffix(".html")+"-screenshots.png")),animations="disabled")
                page.wait_for_function("Array.from(document.images).every(i=>i.complete && i.naturalWidth>0)",timeout=45000)
                assert page.locator(".feature-card").count() == 8
                assert page.locator(".family-card").count() == 4
                assert page.locator("a[href$='.ipk']").count() == 2
                assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), product_page+" "+name+" EN overflow"
                if name == "desktop":
                    page.screenshot(path=str(OUT / (product_page.removesuffix(".html")+"-desktop.png")),full_page=True,animations="disabled")
                page.locator("button[data-lang='sk']").click()
                assert page.locator("html").get_attribute("lang") == "sk"
                assert page.locator(".feature-card .sk:visible").count() == 16
                gallery.first.click()
                assert page.locator("dialog.screenshot-dialog").get_attribute("aria-label")=="Galéria snímok"
                page.locator("dialog.screenshot-dialog button[aria-label=\"Zavrieť\"]").click()
                page.locator("dialog.screenshot-dialog").wait_for(state="detached")
                assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), product_page+" "+name+" SK overflow"
                if name == "mobile":
                    page.screenshot(path=str(OUT / (product_page.removesuffix(".html")+"-mobile-sk.png")),full_page=True,animations="disabled")
                page.locator(".crumb a").click()
                page.wait_for_url("**/index.html#products")
                assert page.locator("html").get_attribute("lang") == "sk"
                page.locator("button[data-lang='en']").click()
                checked.append(product_page)
            page.goto(url.replace('index.html','fullhdglass.html'),wait_until="domcontentloaded")
            cards=page.locator('#screenshots .screenshot-grid figure > a')
            assert cards.count()==14
            assert cards.nth(0).get_attribute('href')=='screenshots/glass/01-full.webp'
            assert cards.nth(1).get_attribute('href')=='fullhdglass-infobars.html'
            assert cards.nth(2).get_attribute('href')=='screenshots/glass/02-full.webp'
            assert cards.nth(3).get_attribute('href')=='fullhdglass-channel-selection.html'
            assert cards.nth(4).get_attribute('href')=='screenshots/glass/03-full.webp'
            cards.nth(1).click()
            page.wait_for_url("**/fullhdglass-infobars.html")
            variants=page.locator("#infobars .screenshot-grid a")
            assert variants.count()==78
            page.evaluate("document.querySelectorAll('img').forEach(i=>i.loading='eager')")
            page.wait_for_function("Array.from(document.images).every(i=>i.complete && i.naturalWidth>0)",timeout=45000)
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), name+" infobar EN overflow"
            variants.first.click()
            dialog=page.locator("dialog.screenshot-dialog")
            assert dialog.is_visible()
            page.wait_for_function("document.querySelector('dialog.screenshot-dialog img').naturalWidth===1920")
            assert "1 / 78" in dialog.locator(".screenshot-caption").inner_text()
            page.keyboard.press("ArrowRight")
            assert "2 / 78" in dialog.locator(".screenshot-caption").inner_text()
            page.keyboard.press("Escape")
            dialog.wait_for(state="detached")
            page.locator("button[data-lang='sk']").click()
            variants.last.click()
            assert "Infobar typu 99" in dialog.locator(".screenshot-caption").inner_text()
            page.wait_for_function("document.querySelector('dialog.screenshot-dialog img').naturalWidth===1920")
            page.keyboard.press("Escape")
            dialog.wait_for(state="detached")
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), name+" infobar SK overflow"
            page.locator(".crumb a").click()
            page.wait_for_url("**/fullhdglass.html#screenshots")
            page.locator('button[data-lang="en"]').click()
            page.locator('#screenshots .screenshot-grid a[href="fullhdglass-channel-selection.html"]').click()
            page.wait_for_url("**/fullhdglass-channel-selection.html")
            channels=page.locator("#channel-selection .screenshot-grid a")
            assert channels.count()==47
            assert [channels.nth(i).get_attribute('data-caption-sk') for i in range(39,45)] == ['s PIG','s PIG 2','s PIG 3','s PIG 4','s PIG 5','s PIG 6']
            page.evaluate("document.querySelectorAll('img').forEach(i=>i.loading='eager')")
            page.wait_for_function("Array.from(document.images).every(i=>i.complete && i.naturalWidth>0)",timeout=45000)
            assert channels.locator("img").evaluate_all("imgs=>imgs.every(i=>i.naturalWidth===Number(i.getAttribute('width')) && i.naturalHeight===Number(i.getAttribute('height')) && i.naturalWidth<440)")
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), name+" channel EN overflow"
            channels.first.click()
            dialog=page.locator("dialog.screenshot-dialog")
            assert "1 / 47" in dialog.locator(".screenshot-caption").inner_text()
            page.wait_for_function("document.querySelector('dialog.screenshot-dialog img').naturalWidth===412")
            page.keyboard.press("ArrowRight")
            assert "2 / 47" in dialog.locator(".screenshot-caption").inner_text()
            page.keyboard.press("Escape")
            dialog.wait_for(state="detached")
            page.locator("button[data-lang='sk']").click()
            channels.last.click()
            assert "s ZZPicon" in dialog.locator(".screenshot-caption").inner_text()
            page.keyboard.press("Escape")
            dialog.wait_for(state="detached")
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), name+" channel SK overflow"
            page.locator(".crumb a").click()
            page.wait_for_url("**/fullhdglass.html#screenshots")
            assert not errors, errors
            report.append({"viewport": name, "width": width, "height": height,
                           "products": 5, "loaded_images": page.locator("img").count(),
                           "languages": ["en","sk"], "overflow": False, "page_errors": errors, "product_pages": checked})
            context.close()
        browser.close()
finally:
    server.shutdown()
(OUT / "report.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
