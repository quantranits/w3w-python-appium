import random

from core.base_page import *


class SearchPage(BasePage):
    NO_RESULTS_FOUND = {'android': (AppiumBy.XPATH, "//android.widget.TextView[@text='No address found.']"), 'ios': ()}
    SEARCH_INPUT = {'android': (AppiumBy.CLASS_NAME, "android.widget.EditText"), 'ios': ()}
    BACK_BUTTON = {'android': (AppiumBy.XPATH, "//*[@content-desc='Back']"), 'ios': ()}
    CLEAR_BUTTON = {'android': (AppiumBy.XPATH, "//*[@content-desc='Clear search history']"), 'ios': ()}
    SCAN_BUTTON = {'android': (AppiumBy.XPATH, "//*[@content-desc='Scan a what3words address']"), 'ios': ()}
    RESULTS_HEADER = {'android': (AppiumBy.XPATH, "//android.widget.TextView[@text='Results']"), 'ios': ()}
    RESULT_ITEMS = {
        'android': (
            AppiumBy.XPATH,
            "//android.widget.TextView[@text='Results']/parent::android.view.View/following-sibling::android.view.View[@clickable='true']",
        ),
        'ios': (),
    }
    RESULT_NAME = {'android': (AppiumBy.XPATH, f"{RESULT_ITEMS['android'][1]}/android.widget.TextView[1]"), 'ios': ()}
    SUGGESTION_CONTAINER = {
        'android': (AppiumBy.XPATH, "//android.widget.TextView[@text='Did you mean?']/parent::android.view.View"),
        'ios': (),
    }
    SUGGESTION_KEYWORD = {
        'android': (AppiumBy.XPATH, f"{SUGGESTION_CONTAINER['android'][1]}/android.widget.TextView[2]"),
        'ios': (),
    }
    SUGGESTION_OK_BTN = {
        'android': (AppiumBy.XPATH, f"{SUGGESTION_CONTAINER['android'][1]}/android.widget.Button[2]"),
    }
    SUGGESTION_CANCEL_BTN = {
        'android': (AppiumBy.XPATH, f"{SUGGESTION_CONTAINER['android'][1]}/android.widget.Button[1]"),
    }

    def __init__(self, driver):
        super().__init__(driver)

    def is_search_page_displayed(self) -> bool:
        """
        Verifies that the search page is displayed.
        """
        return self.is_displayed(self.SEARCH_INPUT, timeout=10)

    def search_with_keyword(self, keyword: str) -> None:
        """
        Clears existing input if any, then enters the search keyword.
        """

        search_field = self.find_element(self.SEARCH_INPUT)
        search_field.clear()
        search_field.send_keys(keyword)

    def get_search_input_text(self) -> str:
        """
        Returns the text of the search input field.
        """
        return self.find_element(self.SEARCH_INPUT).text

    def is_clear_button_displayed(self) -> bool:
        """
        Verifies that the clear button is displayed.
        """
        return self.is_displayed(self.CLEAR_BUTTON, timeout=10)

    def verify_no_result(self) -> bool:
        """
        Verifies that the 'No address found.' text is displayed.
        """
        return self.is_displayed(self.NO_RESULTS_FOUND, timeout=10)

    def verify_has_result(self) -> bool:
        """
        Verifies that the 'Results' header label is present and at least one result item is listed.
        """
        return self.is_displayed(self.RESULT_ITEMS, timeout=10)

    def get_results(self) -> List[Tuple[str, str]]:
        """
        Returns all result elements found on the page.
        """
        return self.find_elements(self.RESULT_ITEMS)

    def result_has_3words(self) -> bool:
        """
        Verifies that each word in the result_name contains the characters
        of the corresponding word in the keyword, in order.
        """
        result_name_elms = self.find_elements(self.RESULT_NAME)
        for result_name_elm in result_name_elms:
            result_name = result_name_elm.text.replace("///", "").lower()
            if len(result_name.split(".")) != 3:
                return False

        return True

    def click_random_result(self) -> str:
        """
        Selects a random item from the search results, taps it, and returns its primary text label.
        """
        results = self.get_results()
        if not results:
            raise Exception("No search results available to click.")

        random_item = random.choice(results)

        # Get primary label text of selected result item for logging/assertion
        title_element = random_item.find_element(AppiumBy.XPATH, ".//android.widget.TextView[1]")
        selected_title = title_element.text

        random_item.click()
        return selected_title

    def click_clear_button(self) -> None:
        """
        Clicks the clear button to clear the search input.
        """
        self.click(self.CLEAR_BUTTON)

    def click_back_button(self) -> None:
        """
        Clicks the back button to navigate back to the home page.
        """
        self.click(self.BACK_BUTTON)

    def is_suggestion_keyword_displayed(self) -> bool:
        """
        Verifies that the suggestion keyword is displayed.
        """
        return self.is_displayed(self.SUGGESTION_KEYWORD, timeout=10)

    def click_suggestion_ok_btn(self) -> None:
        """
        Clicks the suggestion ok button to accept the suggestion.
        """
        self.click(self.SUGGESTION_OK_BTN)

    def click_suggestion_cancel_btn(self) -> None:
        """
        Clicks the suggestion cancel button to reject the suggestion.
        """
        self.click(self.SUGGESTION_CANCEL_BTN)
