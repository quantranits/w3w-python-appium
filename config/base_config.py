"""
Environment configuration — plain module-level variables read from `.env`.
Usage: `from config.base_config import *`
"""

import json
from os import environ
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent.parent
CAPABILITIES_FILE = ROOT_DIR / "config" / "capabilities.json"

ENVIRONMENT = environ.get("ENVIRONMENT", "staging")
PLATFORM = environ.get("PLATFORM", "android").lower()
APPIUM_SERVER_URL = environ.get("APPIUM_SERVER_URL", "http://127.0.0.1:4723")
START_APPIUM_SERVER = environ.get("START_APPIUM_SERVER", "false").lower() == "true"
ENABLE_REPORT = environ.get("ENABLE_REPORT", "true").lower() == "true"

DEVICE_NAME = environ.get("DEVICE_NAME")
PLATFORM_VERSION = environ.get("PLATFORM_VERSION")
UDID = environ.get("UDID")

APP_PATH = environ.get("APP_PATH")
APP_PACKAGE = environ.get("APP_PACKAGE")
APP_ACTIVITY = environ.get("APP_ACTIVITY")
BUNDLE_ID = environ.get("BUNDLE_ID")

# Vendor-specific capability block for a cloud device provider (BrowserStack/Sauce Labs/
# LambdaTest/...), e.g. '{"bstack:options": {"userName": "...", "accessKey": "..."}}'
EXTRA_CAPABILITIES_JSON = environ.get("EXTRA_CAPABILITIES_JSON")


def get_capabilities() -> dict:
    """Return the capabilities dict for PLATFORM, with .env overrides applied."""
    with open(CAPABILITIES_FILE) as f:
        all_caps = json.load(f)

    if PLATFORM not in all_caps:
        raise ValueError(f"No capabilities defined for platform: {PLATFORM}")

    caps = dict(all_caps[PLATFORM])

    overrides = {
        "appium:app": APP_PATH,
        "appium:appPackage": APP_PACKAGE,
        "appium:appActivity": APP_ACTIVITY,
        "appium:bundleId": BUNDLE_ID,
        "appium:deviceName": DEVICE_NAME,
        "appium:platformVersion": PLATFORM_VERSION,
        "appium:udid": UDID
    }
    for key, value in overrides.items():
        if value:
            caps[key] = value

    if EXTRA_CAPABILITIES_JSON:
        caps.update(json.loads(EXTRA_CAPABILITIES_JSON))

    return caps
