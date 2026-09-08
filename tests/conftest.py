import base64
import time
from urllib.parse import urlparse

import allure
import pytest
from appium.webdriver.appium_service import AppiumService

from config.base_config import *
from config.base_config import APPIUM_SERVER_URL, START_APPIUM_SERVER
from config.device_resolver import resolve_capabilities
from core.driver_factory import create_driver
from pages.onboard_page import OnboardPage
from utils.logger import Logger

_appium_service = AppiumService()


def pytest_addoption(parser):
    parser.addoption(
        "--device",
        action="store",
        default="local",
        help="Device to run against: 'local' (default) to auto-detect a connected device "
        "(adb for Android), or a key from config/devices_config.json.",
    )


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """On test failure, attach a screenshot + screen recording directly to the Allure
    test result. Must run here (not in fixture teardown) so Allure links the attachment
    to the test itself instead of filing it under the fixture's Tear Down section."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)

    if rep.when == "call" and rep.failed and ENABLE_REPORT:
        drv = item.funcargs.get("driver")
        if drv is not None:
            allure.attach(
                drv.get_screenshot_as_png(), name="failure_screenshot", attachment_type=allure.attachment_type.PNG
            )
            video_base64 = drv.stop_recording_screen()
            allure.attach(
                base64.b64decode(video_base64), name="failure_video", attachment_type=allure.attachment_type.MP4
            )


@pytest.fixture(autouse=True)
def inject_logger(request):
    """Make `self.logger` available in every test method, matching page-object usage."""
    if request.instance is not None:
        request.instance.logger = Logger()


@pytest.fixture(scope="session")
def device_capabilities(request) -> dict:
    return resolve_capabilities(request.config.getoption("--device"))


@pytest.fixture(scope="session", autouse=True)
def appium_server():
    """Start a local Appium server for the test session when START_APPIUM_SERVER=true.

    Leave disabled (default) when APPIUM_SERVER_URL points at a cloud device
    provider's hub instead — requires Appium installed and on PATH locally.
    """
    if not START_APPIUM_SERVER:
        yield
        return

    parsed = urlparse(APPIUM_SERVER_URL)
    args = ["--address", parsed.hostname or "127.0.0.1", "--port", str(parsed.port or 4723)]
    if parsed.path and parsed.path != "/":
        args += ["--base-path", parsed.path]

    _appium_service.start(args=args)
    yield
    _appium_service.stop()


@pytest.fixture
def driver(appium_server, device_capabilities):
    """Fresh Appium session per test."""
    drv = create_driver(device_capabilities)
    if ENABLE_REPORT:
        drv.start_recording_screen()
    yield drv
    if ENABLE_REPORT:
        try:
            drv.stop_recording_screen()  # already stopped by pytest_runtest_makereport on failure; discard here
        except Exception:
            pass
    drv.quit()


@pytest.fixture(scope='function', autouse=True)
def skip_onboard_flow(driver):
    onboard_page = OnboardPage(driver)
    onboard_page.complete_onboarding_flow()
