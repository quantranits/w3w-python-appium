import pytest
from qase.pytest import qase

from pages.home_page import HomePage
from pages.search_page import SearchPage


@pytest.mark.search
class TestSearchFunctionality:
    @qase.id(57)
    def test_search_entry_from_home_bar(self, driver):
        self.logger.step("Open the home page and tap search bar")
        home_page = HomePage(driver)
        home_page.click_search_bar()

        self.logger.step("Verify user is navigated to search page")
        search_page = SearchPage(driver)
        assert search_page.is_search_page_displayed()
        self.logger.success("Search page displayed successfully")

    @pytest.mark.parametrize("keyword", ["fdcv", "Landmark 81", "Tran Binh Trong", "Trần Bình Trọng"])
    @qase.id(58)
    def test_search_with_standard_place_returns_results(self, driver, keyword):
        self.logger.step("Open the home page")
        home_page = HomePage(driver)
        assert home_page.is_google_map_displayed()
        home_page.click_search_bar()

        self.logger.step(f"Enter standard place keyword: {keyword}")
        search_page = SearchPage(driver)
        search_page.search_with_keyword(keyword)

        self.logger.step("Verify search results are displayed")
        assert search_page.verify_has_result()
        self.logger.success("Search results successfully returned and displayed")

    @pytest.mark.parametrize(
        "keyword", ["///strays.name.morphing", '/limit.broom.flip', '//limit.broom.flip', "///split.the.word   "]
    )
    @qase.id(59)
    def test_search_with_3words_format_returns_results(self, driver, keyword):
        self.logger.step("Open the home page")
        home_page = HomePage(driver)
        assert home_page.is_google_map_displayed()
        home_page.click_search_bar()

        self.logger.step(f"Enter 3-word format keyword: {keyword}")
        search_page = SearchPage(driver)
        search_page.search_with_keyword(keyword)

        self.logger.step("Verify search results are displayed")
        assert search_page.verify_has_result()
        self.logger.success("Search results successfully returned and displayed")

    @pytest.mark.parametrize("keyword", ["invalid keyword", "&^%%*^^&GBBNJ"])
    @qase.id(60)
    def test_search_with_invalid_keyword_shows_no_results(self, driver, keyword):
        self.logger.step("Open the home page")
        home_page = HomePage(driver)
        home_page.click_search_bar()

        self.logger.step("Enter an invalid keyword")
        search_page = SearchPage(driver)
        search_page.search_with_keyword(keyword)

        self.logger.step("Verify the no results found message is visible")
        assert search_page.verify_no_result()
        self.logger.success("No results found message is visible")

    @pytest.mark.parametrize("keyword", ["   ///split.the.word", "//limit broom flip", "/limit broom flip"])
    @qase.id(61)
    def test_search_with_malformed_3words_shows_no_results(self, driver, keyword):
        self.logger.step("Open the home page")
        home_page = HomePage(driver)
        home_page.click_search_bar()

        self.logger.step(f"Enter malformed keyword: {keyword}")
        search_page = SearchPage(driver)
        search_page.search_with_keyword(keyword)

        self.logger.step("Verify the no results found message is visible")
        assert search_page.verify_no_result()
        self.logger.success("No results found message is visible")

    @qase.id(62)
    def test_search_with_3_words_format_returns_results(self, driver):
        self.logger.step("Open the home page")
        home_page = HomePage(driver)
        home_page.click_search_bar()

        self.logger.step("Enter a 3 words format keyword")
        search_page = SearchPage(driver)
        search_page.search_with_keyword("///limit.broom.flip")

        self.logger.step("Verify search results are displayed")
        assert search_page.verify_has_result()
        self.logger.success("Search results successfully returned and displayed")

        assert len(search_page.get_results()) == 3
        self.logger.success("3 search results successfully returned and displayed")

    @qase.id(63)
    def test_select_random_search_result_navigates_to_details(self, driver):
        self.logger.step("Open the home page and search for 'fdcv'")
        home_page = HomePage(driver)
        current_address = home_page.get_3words_address()
        home_page.click_search_bar()

        search_page = SearchPage(driver)
        search_page.search_with_keyword("fdcv")

        self.logger.step("Select a random item from the results list")
        selected_title = search_page.click_random_result()

        self.logger.step("Verify location details bottom sheet is displayed")
        assert home_page.is_google_map_displayed()
        assert current_address != home_page.get_3words_address()

    @qase.id(64)
    def test_clear_search_input(self, driver):
        self.logger.step("Open the home page")
        home_page = HomePage(driver)
        home_page.click_search_bar()

        self.logger.step("Enter a search term")
        search_page = SearchPage(driver)
        search_page.search_with_keyword("dhd66dh")

        self.logger.step("Click clear button")
        search_page.click_clear_button()

        self.logger.step("Verify search input is cleared")
        assert search_page.get_search_input_text() == ""
        self.logger.success("Search input field cleared successfully")

    @qase.id(65)
    def test_navigate_back_from_search_to_home(self, driver):
        self.logger.step("Open search page from home")
        home_page = HomePage(driver)
        home_page.click_search_bar()

        self.logger.step("Click back arrow button")
        search_page = SearchPage(driver)
        search_page.click_back_button()

        self.logger.step("Verify returned to home page")
        assert home_page.is_google_map_displayed()
        self.logger.success("Successfully navigated back to Home page")

    @pytest.mark.parametrize(
        "formatted_input",
        [
            "limit.broom.flip",  # Missing leading slashes
            "  ///limit.broom.flip  ",  # Trailing/leading spaces
            "///limit.broom.fli",  # Incomplete 3rd word
        ],
    )
    @qase.id(66)
    def test_search_format_resilience(self, driver, formatted_input):
        self.logger.step("Open home page and tap search bar")
        home_page = HomePage(driver)
        home_page.click_search_bar()

        self.logger.step(f"Enter formatted variation: '{formatted_input}'")
        search_page = SearchPage(driver)
        search_page.search_with_keyword(formatted_input)

        self.logger.step("Verify app normalizes input and yields valid suggestions")
        assert search_page.verify_has_result()
        self.logger.success("Input format handled successfully")

        assert search_page.result_has_3words()

    @qase.id(67)
    def test_clear_button_visibility_lifecycle(self, driver):
        self.logger.step("Open search page")
        home_page = HomePage(driver)
        home_page.click_search_bar()
        search_page = SearchPage(driver)

        self.logger.step("Verify clear button is NOT visible on empty input")
        assert not search_page.is_clear_button_displayed()

        self.logger.step("Type text and verify clear button becomes visible")
        search_page.search_with_keyword("test")
        assert search_page.is_clear_button_displayed()

        self.logger.step("Tap clear button and verify it hides again")
        search_page.click_clear_button()
        assert not search_page.is_clear_button_displayed()
        self.logger.success("Clear button visibility lifecycle verified")

    @pytest.mark.parametrize(
        "suggestion_keyword, three_words_address",
        [
            ("limit broom flip", "///limit.broom.flip"),
            ("limit-broom-flip", "///limit.broom.flip"),
            ("///limit broom flip", "///limit.broom.flip"),
        ],
    )
    @qase.id(68)
    def test_suggestion_keyword_displayed(self, driver, suggestion_keyword, three_words_address):
        self.logger.step("Open search page")
        home_page = HomePage(driver)
        home_page.click_search_bar()
        search_page = SearchPage(driver)

        search_page.search_with_keyword(suggestion_keyword)

        self.logger.step("Verify suggestion keyword is displayed")
        assert search_page.is_suggestion_keyword_displayed()
        self.logger.success("Suggestion keyword displayed successfully")
        search_page.click_suggestion_ok_btn()

        assert home_page.is_google_map_displayed()
        assert home_page.get_3words_address() == three_words_address

    @pytest.mark.parametrize(
        "raw_keyword, formatted_keyword",
        [
            ("limit broom flip", "///limit.broom.flip"),
        ],
    )
    @qase.id(69)
    def test_suggestion_cancel_reformats_keyword_and_stays_on_search(self, driver, raw_keyword, formatted_keyword):
        self.logger.step("Open search page")
        home_page = HomePage(driver)
        home_page.click_search_bar()
        search_page = SearchPage(driver)

        self.logger.step(f"Enter raw keyword: {raw_keyword}")
        search_page.search_with_keyword(raw_keyword)

        self.logger.step("Verify suggestion keyword is displayed")
        assert search_page.is_suggestion_keyword_displayed()

        self.logger.step("Click suggestion cancel button")
        search_page.click_suggestion_cancel_btn()

        self.logger.step("Verify input is reformatted to the what3words address and stays on search page")
        assert search_page.get_search_input_text() == formatted_keyword
        assert search_page.verify_has_result()
        self.logger.success("Cancel button reformatted keyword and showed results without leaving search page")
