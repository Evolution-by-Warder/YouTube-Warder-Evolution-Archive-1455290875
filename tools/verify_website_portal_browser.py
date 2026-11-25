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
                gallery=page.locator("#screenshots .screenshot-grid a")
                expected={"fullhdglass.html":5,"piconhub.html":3,"gsu.html":7,"radio.html":10,"youtube-warder.html":8}
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
            page.locator('#screenshots a[href="fullhdglass-infobars.html"]').click()
            page.wait_for_url("**/fullhdglass-infobars.html")
            variants=page.locator("#infobars .screenshot-grid a")
            assert variants.count()==77
            page.evaluate("document.querySelectorAll('img').forEach(i=>i.loading='eager')")
            page.wait_for_function("Array.from(document.images).every(i=>i.complete && i.naturalWidth>0)",timeout=45000)
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), name+" infobar EN overflow"
            variants.first.click()
            dialog=page.locator("dialog.screenshot-dialog")
            assert dialog.is_visible()
            page.wait_for_function("document.querySelector('dialog.screenshot-dialog img').naturalWidth===1920")
            assert "1 / 77" in dialog.locator(".screenshot-caption").inner_text()
            page.keyboard.press("ArrowRight")
            assert "2 / 77" in dialog.locator(".screenshot-caption").inner_text()
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
