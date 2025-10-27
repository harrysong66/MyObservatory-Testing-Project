from typing import Tuple
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from utils import get_logger

logger = get_logger(__name__)

class SlidePage(BasePage):

    # Android locators
    ANDROID_LOCATORS = {
        "background_image": (
            AppiumBy.ID,
            "hko.MyObservatory_v1_0:id/backgroundImage"
        ),
        "new_radar_imagery_widget": (
            AppiumBy.ACCESSIBILITY_ID,
            "New radar imagery widget"
        ),
        "next_page_btn": (
            AppiumBy.ACCESSIBILITY_ID,
            "Next page"
        ),
        "close_btn": (
            AppiumBy.ACCESSIBILITY_ID,
            "Close"
        ),
    }

    # iOS locators
    IOS_LOCATORS = {
        "background_image": (
            AppiumBy.ID,
            "hko.MyObservatory_v1_0:id/backgroundImage"
        ),
        "new_radar_imagery_widget": (
            AppiumBy.ACCESSIBILITY_ID,
            "New radar imagery widget"
        ),
        "next_page_btn": (
            AppiumBy.ACCESSIBILITY_ID,
            "Next page"
        ),
        "close_btn": (
            AppiumBy.ACCESSIBILITY_ID,
            "Close"
        ),
    }

    def __init__(self, driver):
        """Initialize home page.

        Args:
            driver: Appium WebDriver instance
        """
        super().__init__(driver)
        self.platform = driver.capabilities.get("platformName", "Android").lower()
        self.locators = (
            self.ANDROID_LOCATORS if self.platform == "android" else self.IOS_LOCATORS
        )
        logger.info(f"HomePage initialized for platform: {self.platform}")


    def click_next_page_button(self, timeout: int = 15) -> bool:
        logger.info("Attempting to click next page button")

        if self.click(self.locators["next_page_btn"], timeout, wait_for_clickable=True):
            logger.info("Clicked 'next page' successfully")
            return True

        logger.error("Failed to click next page button")
        return False

    def click_close_button(self, timeout: int = 15) -> bool:
        logger.info("Attempting to click close button")

        if self.click(self.locators["close_btn"], timeout, wait_for_clickable=True):
            logger.info("Clicked 'Close' successfully")
            return True

        logger.error("Failed to click close button")
        return False

    def is_slide_page_displayed(self, timeout: int = 10) -> bool:
        logger.debug("Checking if slide page is displayed")

        # Check for any characteristic element
        is_displayed = (
                self.is_element_visible(self.locators["new_radar_imagery_widget"], timeout) or
                self.is_element_visible(self.locators["next_page_btn"], timeout)
        )

        if is_displayed:
            logger.info("Slide page is displayed")
        else:
            logger.warning("Slide page is not displayed")

        return is_displayed

    def wait_for_slide_page_load(self, timeout: int = 20) -> bool:
        logger.info("Waiting for slide page to load...")

        try:
            # Try multiple characteristic locators before failing
            candidate_locators = [
                self.locators.get("background_image"),
                self.locators.get("new_radar_imagery_widget"),
                self.locators.get("next_page_btn"),
            ]

            for loc in candidate_locators:
                if not loc:
                    continue
                try:
                    self.find_element(loc, timeout, raise_exception=True)
                    logger.info(f"Slide page loaded successfully via locator: {loc}")
                    return True
                except Exception:
                    continue

            raise Exception("None of the slide page characteristic elements were found")
        except Exception as e:
            logger.error(f"Slide page failed to load: {e}")
            return False
