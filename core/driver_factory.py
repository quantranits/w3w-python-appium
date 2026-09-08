"""Creates the Appium WebDriver session from config.base_config."""

from appium import webdriver
from appium.options.common import AppiumOptions

from config.base_config import *


def create_driver(capabilities: dict | None = None):
    """Start a new Appium session.

    Args:
        capabilities: Capabilities dict to use as-is. Defaults to `get_capabilities()`
            (.env-driven) when not provided, e.g. when resolved via --device.
    """
    options = AppiumOptions()
    options.load_capabilities(capabilities or get_capabilities())
    return webdriver.Remote(APPIUM_SERVER_URL, options=options)
