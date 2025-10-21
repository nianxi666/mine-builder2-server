#!/usr/bin/env python3
"""Minimal Selenium + Faker autofill demo for mine-builder2-server."""

from __future__ import annotations

import argparse
import sys
import time
from typing import Dict

from faker import Faker
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

DEFAULT_SELECTORS: Dict[str, str] = {
    "name": "#demo-name",
    "email": "#demo-email",
}


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Autofill demo that uses Selenium + Faker on self-owned or authorized forms. "
            "Stops before any submission or captcha bypass."
        )
    )
    parser.add_argument(
        "--url",
        default="http://localhost:5000/demo-form",
        help="Target form URL. Must be a page you own or are explicitly authorized to automate.",
    )
    parser.add_argument(
        "--selector",
        action="append",
        default=[],
        help=(
            "Override CSS selectors in the form of field=css_selector. Supported fields: "
            "name,email (e.g. --selector name=#custom-name)."
        ),
    )
    parser.add_argument(
        "--headful",
        action="store_true",
        help="Run Chrome in headful mode instead of the default headless mode.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Seconds to wait for each field to become available.",
    )
    parser.add_argument(
        "--wait",
        type=float,
        default=10.0,
        help="Seconds to keep the browser open after autofilling. Use 0 to exit immediately.",
    )
    return parser.parse_args()


def build_selector_map(overrides: list[str]) -> Dict[str, str]:
    selectors = DEFAULT_SELECTORS.copy()
    for override in overrides:
        if "=" not in override:
            raise ValueError(f"Invalid selector override '{override}'. Expected format field=css_selector.")
        field, css_selector = override.split("=", 1)
        field = field.strip().lower()
        css_selector = css_selector.strip()
        if field not in selectors:
            raise ValueError(f"Unsupported selector field '{field}'. Allowed keys: {', '.join(sorted(selectors))}.")
        if not css_selector:
            raise ValueError(f"CSS selector for '{field}' cannot be empty.")
        selectors[field] = css_selector
    return selectors


def configure_browser(headful: bool) -> webdriver.Chrome:
    options = Options()
    if not headful:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,800")

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def main() -> int:
    args = parse_arguments()

    try:
        selectors = build_selector_map(args.selector)
    except ValueError as exc:
        print(f"[CONFIG] {exc}", file=sys.stderr)
        return 2

    faker = Faker()
    generated_name = faker.name()
    generated_email = faker.ascii_email()
    data_to_fill = {"name": generated_name, "email": generated_email}

    driver: webdriver.Chrome | None = None
    try:
        driver = configure_browser(args.headful)
        driver.get(args.url)

        wait = WebDriverWait(driver, args.timeout)
        name_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selectors["name"])))
        email_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selectors["email"])))

        name_field.clear()
        name_field.send_keys(generated_name)
        email_field.clear()
        email_field.send_keys(generated_email)

        print("✅ 已自动填充以下信息：")
        for key, value in data_to_fill.items():
            print(f"  - {key}: {value}")

        print("\n⚠️ 提醒：脚本不会尝试提交表单，也不会绕过验证码或平台风控。")
        print("   请仅在自有/已授权的页面使用，并在人工核对后自行完成后续步骤。")

        wait_seconds = max(0.0, args.wait)
        if wait_seconds > 0:
            print(f"\n浏览器将在 {wait_seconds:.0f} 秒后关闭，期间可手动完成验证码或进一步演示。")
            time.sleep(wait_seconds)
    except TimeoutException as exc:
        print(
            f"[TIMEOUT] 无法在 {args.timeout} 秒内定位到必需的字段：{exc}",
            file=sys.stderr,
        )
        return 1
    except WebDriverException as exc:
        print(f"[WEBDRIVER] 无法启动或控制浏览器：{exc}", file=sys.stderr)
        return 1
    finally:
        if driver is not None:
            driver.quit()

    return 0


if __name__ == "__main__":
    sys.exit(main())
