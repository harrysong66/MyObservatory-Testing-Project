"""Forecast & Warning page object for MyObservatory app."""

from typing import Tuple

from appium.webdriver.common.appiumby import AppiumBy

from pages.base_page import BasePage
from utils import get_logger

logger = get_logger(__name__)


class NavigationDrawerPage(BasePage):
    """Page object for Forecast & Warning Services page."""

    # ============================================
    # LOCATORS
    # ============================================

    # Android locators
    ANDROID_LOCATORS = {
        "forecast_warning_services": (
            AppiumBy.ACCESSIBILITY_ID,
            'Collapsed\nForecast & Warning Services'
        ),
        "nine_day_forecast": (
            AppiumBy.XPATH,
            '//android.widget.LinearLayout[./*[@text="9-Day Forecast"]]'
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
        """Initialize Forecast & Warning page.
        
        Args:
            driver: Appium WebDriver instance
        """
        super().__init__(driver)
        self.platform = driver.capabilities.get("platformName", "Android").lower()
        self.locators = (
            self.ANDROID_LOCATORS if self.platform == "android" else self.IOS_LOCATORS
        )
        logger.info(f"ForecastWarningPage initialized for platform: {self.platform}")

    # ============================================
    # PAGE METHODS
    # ============================================

    def click_forecast_warning_services(self, timeout: int = 15) -> bool:
        """Click on 'forecast_warning_services' option with fallback.

        Args:
            timeout: Maximum wait time

        Returns:
            True if clicked successfully, False otherwise
        """
        logger.info("Attempting to click 'forecast_warning_services'")

        if self.click(self.locators["forecast_warning_services"], timeout, wait_for_clickable=True):
            logger.info("Clicked 'forecast_warning_services' successfully")
            return True

        logger.error("Failed to click 'forecast_warning_services'")
        return False

    def click_nine_day_forecast(self, timeout: int = 15) -> bool:
        """Click on '9-Day Forecast' option with fallback.

        Args:
            timeout: Maximum wait time

        Returns:
            True if clicked successfully, False otherwise
        """
        logger.info("Attempting to click '9-Day Forecast'")

        if self.click(self.locators["nine_day_forecast"], timeout, wait_for_clickable=True):
            logger.info("Clicked '9-Day Forecast' successfully")
            return True

        logger.error("Failed to click '9-Day Forecast'")
        return False


    def is_page_displayed(self, timeout: int = 10) -> bool:
        """Verify Forecast & Warning page is displayed.
        
        Args:
            timeout: Maximum wait time
            
        Returns:
            True if page displayed, False otherwise
        """
        logger.debug("Checking if Forecast & Warning page is displayed")
        
        is_displayed = self.is_element_visible(self.locators["forecast_warning_services"], timeout)
        
        if is_displayed:
            logger.info("Forecast & Warning page is displayed")
        else:
            logger.warning("Forecast & Warning page is not displayed")
        
        return is_displayed
