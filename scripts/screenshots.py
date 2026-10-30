"""Capture README screenshots from the running stack (headless Chromium).

    docker compose up -d --build
    uv run --with playwright python scripts/screenshots.py
"""

import os
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = "docs/screenshots"
APP = os.getenv("APP_URL", "http://localhost:3000")
API = os.getenv("API_URL", "http://localhost:8000")
SAMPLES = Path(__file__).resolve().parent.parent / "samples"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1280, "height": 820})

    page.goto(APP)
    page.wait_for_selector("text=alex_rivera_data_engineer.pdf")
    page.screenshot(path=f"{OUT}/app-home.png")

    page.click("text=alex_rivera_data_engineer.pdf")
    page.wait_for_selector(".chip")
    page.screenshot(path=f"{OUT}/app-parsed-pdf.png", full_page=True)

    # real file upload through the <input type=file>
    page.set_input_files("input[type=file]", str(SAMPLES / "samira_haddad_ml_engineer.docx"))
    page.wait_for_selector("text=samira.haddad@example.com")
    page.screenshot(path=f"{OUT}/app-upload-docx.png", full_page=True)

    with tempfile.TemporaryDirectory() as d:
        bad = Path(d) / "corrupted.pdf"
        bad.write_bytes(b"%PDF-1.4 this is not really a pdf")
        page.set_input_files("input[type=file]", str(bad))
        page.wait_for_selector(".card.error")
        page.screenshot(path=f"{OUT}/app-error.png")

    page.goto(f"{API}/docs")
    page.wait_for_selector(".opblock-summary-path")
    page.wait_for_timeout(500)
    page.screenshot(path=f"{OUT}/api-docs.png")
    browser.close()
