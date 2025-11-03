"""Home page object for MyObservatory app."""
from datetime import datetime
from pathlib import Path

from appium.webdriver.common.appiumby import AppiumBy

from pages.base_page import BasePage
from utils import get_logger
from utils.screenshot_helper import get_screenshot_helper

logger = get_logger(__name__)


class HomePage(BasePage):
    # Android locators
    ANDROID_LOCATORS = {
        # Primary: tolerate hidden bidi chars around content-desc using contains()
        "hamburger_menu_button_desc_contains": (
            AppiumBy.XPATH,
            "//android.widget.ImageButton[contains(@content-desc, 'Navigate up')]"
        ),
        # Fallback: the first ImageButton inside toolbar container
        "hamburger_menu_button_toolbar_first": (
            AppiumBy.XPATH,
            "//android.view.ViewGroup[@resource-id='hko.MyObservatory_v1_0:id/toolbar']//android.widget.ImageButton[1]"
        ),
        # Fallback: UIAutomator descriptionContains
        "hamburger_menu_button_uiautomator": (
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().className("android.widget.ImageButton").descriptionContains("Navigate up")'
        ),
        # A stable title in the toolbar to assert Home is shown
        "home_title_text": (
            AppiumBy.XPATH,
            "//android.widget.TextView[@text='MyObservatory']"
        ),
    }

    # iOS locators
    IOS_LOCATORS = {
        "hamburger_menu_button": (
            AppiumBy.XPATH,
            '//android.widget.ImageButton[@content-desc="Navigate up"]'
        ),
    }

    def __init__(self, driver):
        super().__init__(driver)
        self.platform = driver.capabilities.get("platformName", "Android").lower()
        self.locators = (
            self.ANDROID_LOCATORS if self.platform == "android" else self.IOS_LOCATORS
        )
        logger.info(f"HomePage initialized for platform: {self.platform}")

    def click_hamburger_menu_button(self, timeout: int = 15) -> bool:
        logger.info("Attempting to click hamburger_menu_button")
        candidates = [
            self.locators.get("hamburger_menu_button_desc_contains"),
            self.locators.get("hamburger_menu_button_toolbar_first"),
            self.locators.get("hamburger_menu_button_uiautomator"),
        ]

        for idx, locator in enumerate([c for c in candidates if c]):
            logger.debug(f"Trying hamburger locator candidate {idx+1}: {locator}")
            if self.click(locator, timeout, wait_for_clickable=True):
                logger.info("Clicked 'hamburger menu button' successfully")
                return True

        logger.error("Failed to click hamburger_menu_button with all locator candidates")
        return False


    def wait_for_home_page_load(self, timeout: int = 20) -> bool:
        logger.info("Waiting for home page to load...")
        
        try:
            # Wait for either the toolbar title or any hamburger locator to appear
            title_locator = self.locators.get("home_title_text")
            if title_locator and self.is_element_present(title_locator, timeout):
                logger.info("Home title detected")
                return True

            hamburger_locator = self.locators.get("hamburger_menu_button_desc_contains")
            if hamburger_locator:
                self.find_element_with_retry(
                    hamburger_locator, retries=2, timeout=timeout
                )
            logger.info("Home page loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Home page failed to load: {e}")
            # Debug artifacts: page source + screenshot
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                ps_dir = Path("reports/page_source")
                ps_dir.mkdir(parents=True, exist_ok=True)
                ps_path = ps_dir / f"home_page_source_{timestamp}.xml"
                with open(ps_path, "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                logger.info(f"Saved page source to: {ps_path}")
            except Exception as pe:
                logger.error(f"Failed to save page source: {pe}")

            try:
                sh = get_screenshot_helper(self.driver)
                sh.capture_screenshot(f"home_page_load_failed_{timestamp}.png")
            except Exception as se:
                logger.error(f"Failed to capture screenshot: {se}")
            return False
