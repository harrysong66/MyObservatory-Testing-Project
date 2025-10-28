from typing import Tuple
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from utils import get_logger

logger = get_logger(__name__)

class AgreementPage(BasePage):

    # Android locators
    ANDROID_LOCATORS = {
        "txt_content": (
            AppiumBy.ID,
            "hko.MyObservatory_v1_0:id/txt_content"
        ),
        "agree_button": (
            AppiumBy.ID,
            "hko.MyObservatory_v1_0:id/btn_agree"
        ),
        "confirm_btn": (
            AppiumBy.ID,
            "android:id/button1"
        )
    }

    # iOS locators
    IOS_LOCATORS = {
        "txt_content": (
            AppiumBy.ID,
            "hko.MyObservatory_v1_0:id/txt_content"
        ),
        "agree_button": (
            AppiumBy.ID,
            "hko.MyObservatory_v1_0:id/btn_agree"
        ),
    }

    def __init__(self, driver):
        super().__init__(driver)
        self.platform = driver.capabilities.get("platformName", "Android").lower()
        self.locators = (
            self.ANDROID_LOCATORS if self.platform == "android" else self.IOS_LOCATORS
        )
        logger.info(f"HomePage initialized for platform: {self.platform}")


    def click_agree_button(self, timeout: int = 15) -> bool:
        logger.info("Attempting to click agree button")
        import time
        time.sleep(5)  # Wait for potential animations to complete
        logger.warning(self.driver.context)

        if self.click(self.locators["agree_button"], timeout, wait_for_clickable=True):
            logger.info("Clicked 'agree button' successfully")
            return True

        logger.error("Failed to click agree button")
        return False

    def click_confirm_btn(self, timeout: int = 15) -> bool:
        logger.info("Attempting to click confirm button")
        import time
        time.sleep(5)  # Wait for potential animations to complete
        logger.warning(self.driver.context)

        if self.click(self.locators["confirm_btn"], timeout, wait_for_clickable=True):
            logger.info("Clicked 'confirm button' successfully")
            return True

        logger.error("Failed to click confirm button")
        return False


    def is_agreement_page_displayed(self, timeout: int = 10) -> bool:
        logger.debug("Checking if agreement page is displayed")

        # Check for any characteristic element
        is_displayed = (
                self.is_element_visible(self.locators["txt_content"], timeout) or
                self.is_element_visible(self.locators["agree_button"], timeout)
        )

        if is_displayed:
            logger.info("Agreement page is displayed")
        else:
            logger.warning("Agreement page is not displayed")

        return is_displayed

    def wait_for_agreement_page_load(self, timeout: int = 20) -> bool:
        logger.info("Waiting for agreement page to load...")

        try:
            # Try multiple characteristic locators before failing
            candidate_locators = [
                self.locators.get("txt_content"),
                self.locators.get("agree_button"),
            ]

            for loc in candidate_locators:
                if not loc:
                    continue
                try:
                    self.find_element(loc, timeout, raise_exception=True)
                    logger.info(f"Agreement page loaded successfully via locator: {loc}")
                    return True
                except Exception:
                    # Try next locator
                    continue

            raise Exception("None of the agreement page characteristic elements were found")
        except Exception as e:
            logger.error(f"Agreement page failed to load: {e}")
            return False