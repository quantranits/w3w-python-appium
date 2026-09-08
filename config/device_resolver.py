"""Resolve Appium capabilities for a --device CLI selection against devices_config.json."""

import json
from pathlib import Path

from config.base_config import PLATFORM, get_capabilities
from utils.adb import get_connected_android_udid

DEVICES_CONFIG_FILE = Path(__file__).resolve().parent / "devices_config.json"


def _load_devices() -> dict:
    with open(DEVICES_CONFIG_FILE) as f:
        return json.load(f).get("mobile_devices", {})


def _platform_name(platform: str) -> str:
    return "iOS" if platform.lower() == "ios" else platform.capitalize()


def resolve_capabilities(device_key: str | None) -> dict:
    """Build the Appium capabilities dict for a --device selection.

    - None (flag omitted): unchanged, purely .env-driven `get_capabilities()`.
    - "local": auto-detect a connected device for PLATFORM (adb for Android; iOS still
      relies on UDID/DEVICE_NAME in .env since there is no local iOS auto-detection here).
    - Any other key: looked up in config/devices_config.json's "mobile_devices".
    """
    if device_key is None:
        return get_capabilities()

    if device_key == "local":
        device = {"runMode": "local", "platformName": _platform_name(PLATFORM)}
    else:
        devices = _load_devices()
        if device_key not in devices:
            raise ValueError(f"Unknown --device '{device_key}'. Known devices: {list(devices)}, or 'local'.")
        device = devices[device_key]

    caps = get_capabilities()
    platform_name = device.get("platformName", caps.get("platformName", "Android"))
    caps["platformName"] = platform_name

    if "appium:udid" in device:
        caps["appium:udid"] = device["appium:udid"]
    elif device.get("runMode") == "local" and platform_name.lower() == "android":
        caps["appium:udid"] = get_connected_android_udid()

    return caps
