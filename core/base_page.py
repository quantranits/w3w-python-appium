"""
Base page class for Appium mobile page objects.
Provides common wait/interaction helpers shared by all page objects.
"""

import time
from typing import List, Optional, Tuple

from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.logger import Logger

DEFAULT_TIMEOUT = 15
_ELEMENT_STABILITY_DELAY = 0.5


class BasePage:
    """Base class for mobile page objects. Holds the Appium driver directly (no session manager)."""

    def __init__(self, driver):
        self.driver = driver
        self.logger = Logger()

    def get_platform(self) -> str:
        """Return current platform in lowercase ('android' or 'ios')."""
        return self.driver.capabilities.get("platformName", "").lower()

    def is_android(self) -> bool:
        return self.get_platform() == "android"

    def is_ios(self) -> bool:
        return self.get_platform() == "ios"

    def get_locator_for_platform(self, locator_dict: dict) -> Tuple[str, str]:
        """Resolve a {'android': (...), 'ios': (...)} dict to the current platform's locator."""
        platform = self.get_platform()
        if platform not in locator_dict:
            raise ValueError(f"No locator defined for platform: {platform}")
        return locator_dict[platform]

    def find_element(self, locator: Tuple[str, str], timeout: Optional[int] = None):
        if isinstance(locator, dict):
            locator = self.get_locator_for_platform(locator)
        wait_time = timeout if timeout is not None else DEFAULT_TIMEOUT
        try:
            element = WebDriverWait(self.driver, wait_time).until(EC.presence_of_element_located(locator))
            self.logger.info(f"Element found: {locator}")
            return element
        except TimeoutException:
            self.logger.error(f"Element not found: {locator}")
            raise

    def find_elements(self, locator: Tuple[str, str], timeout: Optional[int] = None) -> List:
        if isinstance(locator, dict):
            locator = self.get_locator_for_platform(locator)
        wait_time = timeout if timeout is not None else DEFAULT_TIMEOUT
        try:
            elements = WebDriverWait(self.driver, wait_time).until(EC.presence_of_all_elements_located(locator))
            self.logger.info(f"Elements found: {locator}, count: {len(elements)}")
            return elements
        except TimeoutException:
            self.logger.info(f"Elements not found: {locator}")
            return []

    def click(self, locator: Tuple[str, str], timeout: Optional[int] = None):
        if isinstance(locator, dict):
            locator = self.get_locator_for_platform(locator)
        wait_time = timeout if timeout is not None else DEFAULT_TIMEOUT
        element = WebDriverWait(self.driver, wait_time).until(EC.element_to_be_clickable(locator))
        element.click()
        self.logger.info(f"Clicked element: {locator}")

    def click_by_platform(self, locator_dict: dict, timeout: Optional[int] = None):
        """Click using a {'android': (...), 'ios': (...)} locator dict."""
        self.click(self.get_locator_for_platform(locator_dict), timeout)

    def send_keys(self, locator: Tuple[str, str], text: str, clear_first: bool = True, timeout: Optional[int] = None):
        element = self.find_element(locator, timeout)
        if clear_first:
            element.clear()
        element.send_keys(text)
        self.logger.info(f"Sent keys to element: {locator}")

    def send_keys_by_platform(
        self, locator_dict: dict, text: str, clear_first: bool = True, timeout: Optional[int] = None
    ):
        self.send_keys(self.get_locator_for_platform(locator_dict), text, clear_first, timeout)

    def get_text(self, locator: Tuple[str, str], timeout: Optional[int] = None) -> str:
        return self.find_element(locator, timeout).text

    def is_displayed(self, locator: Tuple[str, str] | dict, timeout: Optional[int] = None) -> bool:
        if isinstance(locator, dict):
            locator = self.get_locator_for_platform(locator)
        wait_time = timeout if timeout is not None else DEFAULT_TIMEOUT
        try:
            WebDriverWait(self.driver, wait_time).until(EC.visibility_of_element_located(locator))
            return True
        except WebDriverException:
            return False

    def tap_if_present(self, locator: Tuple[str, str] | dict, timeout: int = 3) -> bool:
        """Tap the element if it appears within `timeout`; no-op if it never shows up.

        Use for optional, transient UI (e.g. a one-time OS permission dialog) that a
        test cannot assert on since it may or may not appear.
        """
        if isinstance(locator, dict):
            locator = self.get_locator_for_platform(locator)
        if self.is_displayed(locator, timeout=timeout):
            self.click(locator, timeout=timeout)
            return True
        return False

    def is_enabled(self, locator: Tuple[str, str] | dict, timeout: Optional[int] = None) -> bool:
        if isinstance(locator, dict):
            locator = self.get_locator_for_platform(locator)
        try:
            return self.find_element(locator, timeout).is_enabled()
        except WebDriverException:
            return False

    def wait_for_visible(self, locator: Tuple[str, str] | dict, timeout: Optional[int] = None):
        """Block until the element is visible. Use for wait_for_* readiness checks."""
        if isinstance(locator, dict):
            locator = self.get_locator_for_platform(locator)
        wait_time = timeout if timeout is not None else DEFAULT_TIMEOUT
        return WebDriverWait(self.driver, wait_time).until(EC.visibility_of_element_located(locator))

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: int = 800):
        self.driver.swipe(start_x, start_y, end_x, end_y, duration)
        self.logger.info(f"Swiped from ({start_x}, {start_y}) to ({end_x}, {end_y})")

    def scroll_to_element(self, locator: Tuple[str, str], max_swipes: int = 5) -> bool:
        """Swipe up repeatedly until the element is found, or give up after max_swipes."""
        try:
            if self.find_element(locator, timeout=1).is_displayed():
                return True
        except Exception:
            pass

        size = self.driver.get_window_size()
        start_x = size["width"] // 2
        start_y = int(size["height"] * 0.8)
        end_y = int(size["height"] * 0.2)

        for _ in range(max_swipes):
            self.swipe(start_x, start_y, start_x, end_y)
            time.sleep(_ELEMENT_STABILITY_DELAY)
            try:
                if self.find_element(locator, timeout=1).is_displayed():
                    return True
            except Exception:
                continue
        return False

    def hide_keyboard(self):
        try:
            self.driver.hide_keyboard()
        except Exception as e:
            self.logger.warn(f"Could not hide keyboard: {e}")

    def take_screenshot(self, filename: str) -> str:
        import os

        os.makedirs("reports/screenshots", exist_ok=True)
        filepath = f"reports/screenshots/{filename}.png"
        self.driver.save_screenshot(filepath)
        self.logger.info(f"Screenshot saved: {filepath}")
        return filepath
