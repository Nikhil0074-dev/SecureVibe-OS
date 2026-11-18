#!/usr/bin/env python3
"""Real browser test of the running web app (needs full stack + `next start` on :3000). Saves REAL screenshots."""
import pathlib, sys
from playwright.sync_api import sync_playwright, expect

OUT = pathlib.Path(__file__).resolve().parents[1] / "docs" / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)
URL = "http://localhost:3000/project/demo"
fails = []


def check(name, fn):
    try:
        fn()
        print("  PASS ", name)
    except Exception as e:  # noqa: BLE001
        fails.append(name)
        print("  FAIL ", name, str(e)[:160])


with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1500, "height": 860}, device_scale_factor=1.5)
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)[:150]))
    pg.goto(URL)
    pg.wait_for_selector(".monaco-editor", timeout=30000)
    check("monaco editor loads locally (no CDN)", lambda: expect(pg.locator(".monaco-editor").first).to_be_visible())
    pg.screenshot(path=str(OUT / "08-live-web-initial.png"))

    # ---- Path 1: natural language ("vibe") ----
    pg.get_by_role("button", name="Vibe it").click()
    check("pipeline completes with 100/100", lambda: expect(pg.get_by_text("100/100")).to_be_visible(timeout=40000))
    check("no policy violations shown", lambda: expect(pg.get_by_text("No policy violations")).to_be_visible())
    check("IR rendered onto canvas (4 nodes, 1 edge)", lambda: (expect(pg.locator(".react-flow__node")).to_have_count(4), expect(pg.locator(".react-flow__edge")).to_have_count(1)))
    check("cost shown", lambda: expect(pg.get_by_text("/month")).to_be_visible())
    check("pipeline steps listed", lambda: expect(pg.get_by_text("security:done")).to_be_visible())
    pg.wait_for_timeout(1200)
    check("generated Terraform in editor", lambda: expect(pg.locator(".monaco-editor .view-lines")).to_contain_text("SecureVibe"))
    pg.get_by_role("button", name="providers.tf").click()
    pg.wait_for_timeout(600)
    check("switch file tab", lambda: expect(pg.locator(".monaco-editor .view-lines")).to_contain_text("required_providers"))
    pg.get_by_role("button", name="main.tf").click()
    pg.wait_for_timeout(600)
    pg.screenshot(path=str(OUT / "09-live-vibe-generation.png"))

    # ---- Path 2: draw on canvas ----
    pg.reload()
    pg.wait_for_selector(".monaco-editor", timeout=30000)
    for label in ["+ VPC", "+ EC2", "+ RDS", "+ S3"]:
        pg.get_by_role("button", name=label, exact=True).click()
    check("4 nodes on canvas", lambda: expect(pg.locator(".react-flow__node")).to_have_count(4))
    pg.get_by_role("button", name="Generate from canvas").click()
    check("canvas generation completes", lambda: expect(pg.get_by_text("100/100")).to_be_visible(timeout=40000))
    pg.wait_for_timeout(1200)
    pg.screenshot(path=str(OUT / "10-live-canvas-generation.png"))

    def no_errors():
        if errors:
            raise AssertionError(errors)

    check("no uncaught page errors", no_errors)
    b.close()

print("\nALL UI CHECKS PASSED" if not fails else f"\n{len(fails)} FAILED: {', '.join(fails)}")
sys.exit(1 if fails else 0)
