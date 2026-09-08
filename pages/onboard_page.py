from core.base_page import *


class OnboardPage(BasePage):
    # Ad Banner Locators
    DISMISS_BANNER_BTN = {
        "android": (AppiumBy.ACCESSIBILITY_ID, "Dismiss"),
        "ios": (AppiumBy.XPATH, "//ios.widget.Button[@name='Dismiss']"),
    }

    # Language Page Locators
    LANGUAGE_TITLE = {
        "android": (AppiumBy.XPATH, "//android.widget.TextView[@text='Select your language']"),
        "ios": (AppiumBy.XPATH, "//ios.widget.TextView[@name='Select your language']"),
    }

    LANGUAGE_OPTION = {
        "android": (AppiumBy.XPATH, "//android.widget.TextView[@text='%s']"),
        "ios": (AppiumBy.XPATH, "//ios.widget.TextView[@name='%s']"),
    }

    # Login/Signup Page Locators
    LOGIN_TITLE = {
        "android": (AppiumBy.XPATH, "//android.widget.TextView[@text='Join what3words today']"),
        "ios": (AppiumBy.XPATH, "//ios.widget.TextView[@name='Join what3words today']"),
    }

    BACK_BTN = {
        "android": (AppiumBy.ID, "com.what3words.android:id/toolbarBackIcon"),
        "ios": (AppiumBy.XPATH, "//ios.widget.Button[@name='Back']"),
    }

    def __init__(self, driver):
        super().__init__(driver)

    def dismiss_ad_banner(self):
        """Wait for and dismiss the ad banner if it appears."""
        if self.is_displayed(self.DISMISS_BANNER_BTN, timeout=5):
            self.click(self.DISMISS_BANNER_BTN)

    def select_language(self, language):
        """Select English (UK) from the language selection screen."""
        if self.is_displayed(self.LANGUAGE_TITLE, timeout=5):
            locator = self.get_locator_for_platform(self.LANGUAGE_OPTION)
            self.find_element((locator[0], locator[1] % language)).click()

    def close_login_page(self):
        """Click back to close the login/signup screen and load the Home page."""
        if self.is_displayed(self.LOGIN_TITLE, timeout=5):
            self.click(self.BACK_BTN)

    def complete_onboarding_flow(self):
        """Combined full onboarding execution flow."""
        self.dismiss_ad_banner()
        self.select_language('English (UK)')
        self.close_login_page()
