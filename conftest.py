from pathlib import Path
from typing import Generator

import pytest
from _pytest.config import Config
from _pytest.nodes import Item

from config import config as app_config
from drivers import create_driver, quit_driver
from utils import get_logger, get_screenshot_helper

logger = get_logger(__name__)


# --------------------------------------------
# pytest hooks
# --------------------------------------------


def pytest_configure(config: Config) -> None:
    # Ensure required directories exist
    for directory in ["logs", "reports", "reports/screenshots"]:
        Path(directory).mkdir(parents=True, exist_ok=True)

    logger.info("=" * 80)
    logger.info("TEST EXECUTION STARTED")
    logger.info(f"Platform: {app_config.test.platform}")
    logger.info(f"Appium URL: {app_config.get_appium_url()}")
    logger.info("=" * 80)


def pytest_collection_modifyitems(config: Config, items: list[Item]) -> None:
    # Add platform marker automatically based on TEST_PLATFORM
    platform = app_config.test.platform.lower()

    for item in items:
        # Auto-mark tests based on platform
        if "test_mobile" in item.nodeid or "myobservatory" in item.nodeid.lower():
            if platform == "android":
                item.add_marker(pytest.mark.android)
                item.add_marker(pytest.mark.mobile)
            elif platform == "ios":
                item.add_marker(pytest.mark.ios)
                item.add_marker(pytest.mark.mobile)

        # Auto-mark API tests
        if "test_api" in item.nodeid or "api" in item.nodeid.lower():
            item.add_marker(pytest.mark.api)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: Item, call):

    outcome = yield
    report = outcome.get_result()

    # Capture screenshot on failure for mobile tests
    if report.when == "call" and report.failed:
        # Check if driver fixture was used
        if hasattr(item, "funcargs") and "driver" in item.funcargs:
            driver = item.funcargs["driver"]

            if driver and app_config.test.capture_screenshot:
                try:
                    screenshot_helper = get_screenshot_helper(driver)
                    screenshot_path = screenshot_helper.capture_screenshot_on_failure(item.nodeid)

                    if screenshot_path:
                        logger.info(f"Screenshot captured: {screenshot_path}")
                        # Attach to report if using pytest-html
                        if hasattr(report, "extra"):
                            report.extra = getattr(report, "extra", [])
                            report.extra.append(pytest.html.image(screenshot_path))
                except Exception as e:
                    logger.error(f"Failed to capture screenshot: {e}")


# -------------------------------------------
# configuration fixtures
# -------------------------------------------


@pytest.fixture(scope="session")
def test_config():
    logger.info("Loading test configuration...")
    yield app_config
    logger.info("Test configuration cleanup complete")


@pytest.fixture(scope="session")
def platform(test_config) -> str:
    return test_config.test.platform


# -------------------------------------------
# driver fixtures (session-scoped)
# -------------------------------------------


@pytest.fixture(scope="session")
def driver(test_config) -> Generator:
    logger.info(f"Creating driver for platform: {test_config.test.platform}")

    driver_instance = None
    try:
        driver_instance = create_driver()
        logger.info("Driver created successfully")
        yield driver_instance
    except Exception as e:
        logger.error(f"Failed to create driver: {e}")
        pytest.fail(f"Driver creation failed: {e}")
    finally:
        quit_driver(driver_instance)


# -------------------------------------------
# helper fixtures
# -------------------------------------------


@pytest.fixture(scope="function")
def wait_helper(driver):
    from utils import WaitHelper

    timeout = app_config.test.explicit_wait
    return WaitHelper(driver, timeout=timeout)


@pytest.fixture(scope="function")
def screenshot_helper(driver):
    return get_screenshot_helper(driver)


# -------------------------------------------
# page object fixtures (injected with driver)
# -------------------------------------------


@pytest.fixture(scope="function")
def agreement_page(driver):
    from pages.agreement_page import AgreementPage
    return AgreementPage(driver)


@pytest.fixture(scope="function")
def slide_page(driver):
    from pages.slide_page import SlidePage
    return SlidePage(driver)


@pytest.fixture(scope="function")
def home_page(driver):
    from pages.home_page import HomePage
    return HomePage(driver)


@pytest.fixture(scope="function")
def navigation_drawer_page(driver):
    from pages.navigation_drawer_page import NavigationDrawerPage
    return NavigationDrawerPage(driver)


@pytest.fixture(scope="function")
def nine_day_forecast_page(driver):
    from pages.nine_day_forecast_page import NineDayForecastPage
    return NineDayForecastPage(driver)


# -------------------------------------------
# api fixtures
# -------------------------------------------


@pytest.fixture(scope="session")
def api_client():
    from api.weather_api_client import WeatherAPIClient

    client = WeatherAPIClient()
    logger.info("Weather API client created")

    yield client

    logger.info("Weather API client cleanup complete")


# -------------------------------------------
# BDD fixtures
# -------------------------------------------


@pytest.fixture
def context():
    return {}
