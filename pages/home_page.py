from core.base_page import *


class HomePage(BasePage):
    SEARCH_BAR = {
        "android": (AppiumBy.ACCESSIBILITY_ID, "Search bar"),
        "ios": (AppiumBy.ACCESSIBILITY_ID, "Search bar"),
    }
    GOOGLE_MAP_CONTENT = {
        "android": (AppiumBy.XPATH, "//android.view.TextureView[@content-desc='Google Map']"),
        "ios": (),
    }
    LOCATION_3WORDS_ADDRESS = {
        "android": (AppiumBy.XPATH, "//android.widget.TextView[contains(@text, '///')]"),
        "ios": (),
    }
    COPY_ADDRESS_BTN = {
        "android": (
            AppiumBy.XPATH,
            "//android.view.View[@content-desc='copy what3words address']/following-sibling::android.widget.Button",
        ),
        "ios": (),
    }
    SHARE_BTN = {
        "android": (
            AppiumBy.XPATH,
            "//android.widget.TextView[@text='Share']/following-sibling::android.widget.Button",
        ),
        "ios": (),
    }
    NAVIGATION_BTN = {
        "android": (
            AppiumBy.XPATH,
            "//android.widget.TextView[@text='Navigate']/following-sibling::android.widget.Button",
        ),
        "ios": (),
    }
    SAVE_BTN = {
        "android": (AppiumBy.XPATH, "//android.widget.TextView[@text='Save']/following-sibling::android.widget.Button"),
        "ios": (),
    }

    def __init__(self, driver):
        super().__init__(driver)

    def is_google_map_displayed(self) -> bool:
        return self.is_displayed(self.GOOGLE_MAP_CONTENT)

    def click_search_bar(self):
        self.click(self.SEARCH_BAR)

    def get_3words_address(self) -> str:
        return self.get_text(self.LOCATION_3WORDS_ADDRESS)
