from appium.webdriver.common.appiumby import AppiumBy

from pages.base_page import BasePage
from utils import get_logger

logger = get_logger(__name__)


class NavigationDrawerPage(BasePage):

    # Android locators
    ANDROID_LOCATORS = {
        # Prefer visible TextView label; drawer variants might differ by expand state
        "forecast_warning_services_text": (
            AppiumBy.XPATH,
            '//android.widget.TextView[@text="Forecast & Warning Services"]'
        ),
        # Fallback: contains() to tolerate localization artifacts/line breaks
        "forecast_warning_services_text_contains": (
            AppiumBy.XPATH,
            '//android.widget.TextView[contains(@text, "Forecast & Warning Services")]'
        ),
        # Fallback: accessibility id may include state prefix like "Collapsed\n" or "Expanded\n"
        "forecast_warning_services_accessibility_contains": (
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().descriptionContains("Forecast & Warning Services")'
        ),
        "nine_day_forecast": (
            AppiumBy.XPATH,
            '//android.widget.TextView[@resource-id="hko.MyObservatory_v1_0:id/title" and @text="9-Day Forecast"]'
        ),
        # Fallback outside drawer: bottom sheet tab on Home
        "nine_day_forecast_bottom_sheet_tab": (
            AppiumBy.XPATH,
            "//android.widget.LinearLayout[contains(@content-desc, '9-Day Forecast')]"
        ),
        "nine_day_forecast_bottom_sheet_text": (
            AppiumBy.XPATH,
            "//android.widget.TextView[@text='9-Day Forecast']"
        ),
    }

    # iOS locators
    IOS_LOCATORS = {
        "forecast_warning_services": (
            AppiumBy.XPATH,
            '//XCUIElementTypeStaticText[@name="Forecast & Warning Services"]'
        ),
        "nine_day_forecast": (
            AppiumBy.XPATH,
            '//XCUIElementTypeStaticText[@name="9-Day Forecast"]'
        ),
    }

    def __init__(self, driver):
        super().__init__(driver)
        self.platform = driver.capabilities.get("platformName", "Android").lower()
        self.locators = (
            self.ANDROID_LOCATORS if self.platform == "android" else self.IOS_LOCATORS
        )
        logger.info(f"ForecastWarningPage initialized for platform: {self.platform}")

    def _open_drawer_via_edge_swipe(self) -> None:
        try:
            size = self.driver.get_window_size()
            y = size["height"] // 2
            start_x = int(size["width"] * 0.02)
            end_x = int(size["width"] * 0.75)
            self.swipe(start_x, y, end_x, y, duration=400)
            logger.debug("Performed edge swipe to open drawer")
        except Exception as e:
            logger.warning(f"Edge swipe to open drawer failed: {e}")

    def click_forecast_warning_services(self, timeout: int = 15) -> bool:
        logger.info("Attempting to click 'forecast_warning_services'")
        candidates = [
            self.locators.get("forecast_warning_services_text"),
            self.locators.get("forecast_warning_services_text_contains"),
            self.locators.get("forecast_warning_services_accessibility_contains"),
        ]

        # Try once; if not found, try to open drawer via swipe and retry
        for phase in ("initial", "after_swipe"):
            for idx, locator in enumerate([c for c in candidates if c]):
                logger.debug(f"{phase}: Trying drawer locator candidate {idx+1}: {locator}")
                if self.click(locator, timeout if phase == "initial" else 5, wait_for_clickable=True):
                    logger.info("Clicked 'forecast_warning_services' successfully")
                    return True
            if phase == "initial":
                self._open_drawer_via_edge_swipe()

        logger.error("Failed to click 'forecast_warning_services' with all locator candidates")
        return False

    def click_nine_day_forecast(self, timeout: int = 15) -> bool:
        logger.info("Attempting to click '9-Day Forecast'")
        candidates = [
            self.locators.get("nine_day_forecast"),
            self.locators.get("nine_day_forecast_bottom_sheet_tab"),
            self.locators.get("nine_day_forecast_bottom_sheet_text"),
        ]

        # Prefer drawer item first, then fallbacks; attempt swipe-open once if drawer not visible
        for phase in ("initial", "after_swipe"):
            for idx, locator in enumerate([c for c in candidates if c]):
                logger.debug(f"{phase}: Trying 9-Day locator candidate {idx+1}: {locator}")
                if self.click(locator, timeout if phase == "initial" else 5, wait_for_clickable=True):
                    logger.info("Clicked '9-Day Forecast' successfully")
                    return True
            if phase == "initial":
                self._open_drawer_via_edge_swipe()

        logger.error("Failed to click '9-Day Forecast' with all locator candidates")
        return False


    def is_page_displayed(self, timeout: int = 10) -> bool:
        logger.debug("Checking if Forecast & Warning page is displayed")
        anchor = (
            self.locators.get("forecast_warning_services_text")
            or self.locators.get("forecast_warning_services_text_contains")
            or self.locators.get("forecast_warning_services_accessibility_contains")
        )
        is_displayed = self.is_element_visible(anchor, timeout) if anchor else False
        if not is_displayed and anchor:
            self._open_drawer_via_edge_swipe()
            is_displayed = self.is_element_visible(anchor, 5)
        
        if is_displayed:
            logger.info("Forecast & Warning page is displayed")
        else:
            logger.warning("Forecast & Warning page is not displayed")
        
        return is_displayed
