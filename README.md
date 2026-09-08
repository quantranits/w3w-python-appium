# python-appium

Mobile automation framework using Appium + Python + pytest, built for the what3words
technical test.

**Platform:** Android. iOS is partially scaffolded in the Page Object Model (see
[Platform support in Page Objects](#platform-support-in-page-objects-android--ios) below)
but not implemented/verified for this test.

**Task 2 (Share feature test cases):** [`docs/what3words—ShareFeatureTestCases.pdf`](docs/what3words—ShareFeatureTestCases.pdf)

## Tech stack
- Python 3.12, `uv` for package management
- Appium-Python-Client, Selenium
- pytest

## Project structure
```
config/       - base_config.py (env vars, `from config.base_config import *`), capabilities.json
                (per-platform Appium caps), devices_config.json + device_resolver.py (--device selection)
core/         - base_page.py (BasePage with wait/interaction helpers), driver_factory.py
pages/        - Page Object Models, one subfolder per feature/app area
tests/        - pytest tests + conftest.py (driver fixture)
utils/        - shared helpers (logger, etc.)
```

## Setup

### Prerequisites
- **Python 3.12**, installed via [pyenv](https://github.com/pyenv/pyenv) (recommended —
  follow pyenv's own install instructions, then `pyenv install 3.12` and `pyenv local 3.12`
  in this directory).
- **Appium 2.x** — follow the [official quickstart](https://appium.io/docs/en/2.0/quickstart/install/),
  including installing the `uiautomator2` driver for Android (`appium driver install uiautomator2`)
  or `xcuitest` for iOS.
- **Android**: `adb` on `PATH` (from Android SDK platform-tools), a connected device or
  running emulator with the what3words app already installed, and USB debugging enabled.

### Install
```bash
uv sync
cp .env.example .env
# fill in PLATFORM, APP_PATH/APP_PACKAGE/APP_ACTIVITY (Android) or BUNDLE_ID (iOS), DEVICE_NAME, PLATFORM_VERSION
```

## Local device vs. cloud device provider

- **Local device**: keep `APPIUM_SERVER_URL=http://127.0.0.1:4723` and either run `appium`
  manually in a separate terminal, or set `START_APPIUM_SERVER=true` in `.env` — the
  session-scoped `appium_server` fixture in `tests/conftest.py` will launch/stop a local
  Appium server for you (requires Appium installed and on `PATH`).
- **Cloud device provider** (BrowserStack/Sauce Labs/LambdaTest/...): point
  `APPIUM_SERVER_URL` at the provider's hub URL (with embedded credentials if required),
  leave `START_APPIUM_SERVER=false`, and set `EXTRA_CAPABILITIES_JSON` to the provider's
  vendor options block (e.g. `bstack:options`).

## Run tests
```bash
uv run pytest
uv run pytest -m search
uv run pytest tests/test_search_function.py
```

## Selecting a device with --device
Defaults to `local`. Pass `--device` to override device selection without editing `.env`:

- `--device=local` (default) — auto-detects the connected device for `PLATFORM`. For
  Android this runs `adb devices` and uses the single attached device's udid (errors if
  zero or more than one device is connected).
- `--device=<key>` — looks up `<key>` in `config/devices_config.json`'s `mobile_devices`
  (e.g. `local_android`, `cloud_android`) and applies its `platformName`/`appium:udid`.

```bash
uv run pytest -vsk test_search_entry_from_home_bar          # --device=local by default
uv run pytest -vsk test_search_entry_from_home_bar --device=cloud_android
```

## Platform support in Page Objects (Android + iOS)
Every page object defines locators as a `{"android": (...), "ios": (...)}` dict rather than
a single locator, so the same page object class can drive either platform:

```python
SEARCH_BAR = {
    "android": (AppiumBy.ACCESSIBILITY_ID, "Search bar"),
    "ios": (AppiumBy.ACCESSIBILITY_ID, "Search bar"),
}
```

`BasePage.get_platform()` reads `driver.capabilities["platformName"]` at runtime and
`get_locator_for_platform(...)` picks the matching entry from the dict — the platform switch
is automatic, a test/page object never branches on platform itself. The `_by_platform`
helpers (`click_by_platform`, `send_keys_by_platform`, or passing a locator dict straight
into `is_displayed(...)`/`find_element(...)`) resolve this for you.

**Current state:** this test scoped to Android only (per the assignment's "choose either
platform"), so `pages/home_page.py` and `pages/search_page.py` only have real Android
locators — their `"ios"` entries are empty-tuple placeholders (`()`), not implemented.
Running with `PLATFORM=ios` today will raise `ValueError: No locator defined for platform: ios`
the first time one of those pages resolves a locator, rather than silently passing. Only
`pages/onboard_page.py` currently has real locators for both platforms. Adding iOS support
for Search/Home is just a matter of filling in the `"ios"` entries with real locators (e.g.
via Appium Inspector) — no other code changes needed.

## Writing a new page object
1. Create `pages/<feature>/<name>_page.py`, subclass `BasePage`.
2. Define locators as `{"android": (...), "ios": (...)}` dicts (see `pages/onboard_page.py`
   for a page with both platforms implemented, or `pages/search_page.py` for the
   Android-only pattern used in this test).
3. Methods represent user actions and return state — no assertions inside page objects.
4. Access via `self.get_locator_for_platform(...)` / `self.click_by_platform(...)` helpers to stay
   platform-agnostic.

## Writing a new test
- One `driver` fixture per test (function-scoped, auto-quits on teardown) — see `tests/conftest.py`.
- Instantiate page objects directly with the fixture: `HomePage(driver)`.
- Assertions live in the test, not in page objects.
- `self.logger` is auto-injected into every test method (autouse `inject_logger` fixture in
  `tests/conftest.py`) — use `self.logger.step(...)`/`substep(...)`/`success(...)`/`data(...)`
  to log and to show up as steps/attachments in the Allure report (see `pages/home_page.py`,
  `pages/search_page.py`, and `tests/test_search_function.py`).

## Test report (Allure)
Every `pytest` run writes raw results to `reports/allure-results/` (configured via `addopts`
in `pyproject.toml`, cleared each run). `self.logger.step(...)`/`substep(...)` calls show up
as steps in the report.

Screenshot + video capture on failure is gated by **`ENABLE_REPORT`** in `.env` (see
`.env.example`):
- `ENABLE_REPORT=true` — on test failure, a screenshot and a full screen recording (mp4, via
  Appium's `start_recording_screen`/`stop_recording_screen`) are attached to the Allure
  result. See `driver` fixture and `pytest_runtest_makereport` in `tests/conftest.py`.
- `ENABLE_REPORT=false` (default) — no recording/screenshot overhead is added to test runs.

Install the Allure commandline tool once (not a Python dependency):
```bash
brew install allure
```

View the report:
```bash
uv run pytest
allure serve reports/allure-results          # opens an interactive report in the browser
# or: allure generate reports/allure-results -o reports/allure-report --clean
```
