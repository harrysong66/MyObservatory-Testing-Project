"""Home page object for MyObservatory app."""

from typing import Tuple

from appium.webdriver.common.appiumby import AppiumBy

from pages.base_page import BasePage
from utils import get_logger

logger = get_logger(__name__)


class HomePage(BasePage):

    # Android locators
    ANDROID_LOCATORS = {
        "wether_photo": (
            AppiumBy.ID,
            "hko.MyObservatory_v1_0:id/weatherPhoto"
        ),
        "hamburger_menu_button": (
            AppiumBy.XPATH,
            '//android.widget.ImageButton[@content-desc="Navigate up"]'
        ),
    }

    # iOS locators
    IOS_LOCATORS = {
        "wether_photo": (
            AppiumBy.ID,
            "hko.MyObservatory_v1_0:id/weatherPhoto"
        ),
        "hamburger_menu_button": (
            AppiumBy.XPATH,
            '//android.widget.ImageButton[@content-desc="Navigate up"]'
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

    def click_hamburger_menu_button(self, timeout: int = 15) -> bool:
        logger.info("Attempting to click hamburger_menu_button")

        if self.click(self.locators["hamburger_menu_button"], timeout, wait_for_clickable=True):
            logger.info("Clicked 'hamburger menu button' successfully")
            return True
        
        logger.error("Failed to click hamburger_menu_button")
        return False


    def wait_for_home_page_load(self, timeout: int = 20) -> bool:
        """Wait for home page to fully load.
        
        Args:
            timeout: Maximum wait time
            
        Returns:
            True if loaded, False otherwise
        """
        logger.info("Waiting for home page to load...")
        
        try:
            # Wait for key elements to be present
            self.find_element(self.locators["wether_photo"], timeout, raise_exception=True)
            logger.info("Home page loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Home page failed to load: {e}")
            return False
