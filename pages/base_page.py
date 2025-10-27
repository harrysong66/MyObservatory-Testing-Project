from typing import Any, List, Optional, Tuple

from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.support import expected_conditions as EC

from config import config
from utils import WaitHelper, get_logger

logger = get_logger(__name__)


class BasePage:

    def __init__(self, driver: Any):
        self.driver = driver
        self.wait_helper = WaitHelper(
            driver,
            timeout=config.test.explicit_wait,
            poll_frequency=config.get_yaml_value("test", "waits", "polling", default=0.5)
        )
        self.logger = logger


    def find_element(
        self,
        locator: Tuple[str, str],
        timeout: Optional[int] = None,
        raise_exception: bool = True
    ) -> Optional[Any]:
        try:
            self.logger.debug(f"Finding element: {locator}")
            element = self.wait_helper.wait_for_element_present(locator, timeout)
            return element
        except TimeoutException:
            self.logger.warning(f"Element not found: {locator}")
            if raise_exception:
                raise
            return None
        except Exception as e:
            self.logger.error(f"Error finding element {locator}: {e}")
            if raise_exception:
                raise
            return None

    def find_elements(
        self,
        locator: Tuple[str, str],
        timeout: Optional[int] = None
    ) -> List[Any]:
        try:
            self.logger.debug(f"Finding elements: {locator}")
            elements = self.wait_helper.wait_for_elements_present(locator, timeout)
            self.logger.debug(f"Found {len(elements)} elements")
            return elements
        except TimeoutException:
            self.logger.warning(f"No elements found: {locator}")
            return []
        except Exception as e:
            self.logger.error(f"Error finding elements {locator}: {e}")
            return []

    def find_element_with_retry(
        self,
        locator: Tuple[str, str],
        retries: int = 3,
        timeout: Optional[int] = None
    ) -> Optional[Any]:
        for attempt in range(retries):
            try:
                return self.find_element(locator, timeout, raise_exception=True)
            except StaleElementReferenceException:
                self.logger.warning(
                    f"Stale element, retry {attempt + 1}/{retries}: {locator}"
                )
                if attempt == retries - 1:
                    raise
            except TimeoutException:
                if attempt == retries - 1:
                    raise
                self.logger.warning(f"Retry {attempt + 1}/{retries}: {locator}")
        
        return None


    def click(
        self,
        locator: Tuple[str, str],
        timeout: Optional[int] = None,
        wait_for_clickable: bool = True
    ) -> bool:
        try:
            self.logger.debug(f"Clicking element: {locator}")
            
            if wait_for_clickable:
                element = self.wait_helper.wait_for_element_clickable(locator, timeout)
            else:
                element = self.find_element(locator, timeout)
            
            element.click()
            self.logger.debug(f"Clicked element: {locator}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to click element {locator}: {e}")
            
            # Fallback: Try tap action
            try:
                self.logger.info("Attempting fallback tap action...")
                element = self.find_element(locator, timeout, raise_exception=False)
                if element:
                    self.tap_element(element)
                    return True
            except Exception as tap_error:
                self.logger.error(f"Fallback tap also failed: {tap_error}")
            
            return False

    def send_keys(
        self,
        locator: Tuple[str, str],
        text: str,
        clear_first: bool = True,
        timeout: Optional[int] = None
    ) -> bool:

        try:
            self.logger.debug(f"Sending keys to element: {locator}")
            element = self.find_element(locator, timeout)
            
            if element:
                if clear_first:
                    element.clear()
                element.send_keys(text)
                self.logger.debug(f"Sent keys to element: {locator}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to send keys to {locator}: {e}")
            return False

    def get_text(
        self,
        locator: Tuple[str, str],
        timeout: Optional[int] = None
    ) -> str:
        try:
            element = self.find_element(locator, timeout, raise_exception=False)
            if element:
                text = element.text
                self.logger.debug(f"Got text from {locator}: {text}")
                return text
            return ""
        except Exception as e:
            self.logger.error(f"Failed to get text from {locator}: {e}")
            return ""

    def get_attribute(
        self,
        locator: Tuple[str, str],
        attribute: str,
        timeout: Optional[int] = None
    ) -> Optional[str]:

        try:
            element = self.find_element(locator, timeout, raise_exception=False)
            if element:
                value = element.get_attribute(attribute)
                self.logger.debug(f"Got attribute {attribute} from {locator}: {value}")
                return value
            return None
        except Exception as e:
            self.logger.error(f"Failed to get attribute {attribute} from {locator}: {e}")
            return None

    def is_element_visible(
        self,
        locator: Tuple[str, str],
        timeout: Optional[int] = 5
    ) -> bool:
        try:
            element = self.wait_helper.wait_for_element_visible(locator, timeout)
            return element is not None
        except TimeoutException:
            return False
        except Exception as e:
            self.logger.error(f"Error checking visibility of {locator}: {e}")
            return False

    def is_element_present(
        self,
        locator: Tuple[str, str],
        timeout: Optional[int] = 5
    ) -> bool:
        try:
            element = self.find_element(locator, timeout, raise_exception=False)
            return element is not None
        except Exception as e:
            self.logger.error(f"Error checking presence of {locator}: {e}")
            return False


    def tap_element(self, element: Any) -> None:
        try:
            from appium.webdriver.common.touch_action import TouchAction
            
            action = TouchAction(self.driver)
            action.tap(element).perform()
            self.logger.debug("Tapped element")
        except Exception as e:
            self.logger.error(f"Failed to tap element: {e}")
            raise

    def swipe(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration: int = 1000
    ) -> None:
        try:
            self.driver.swipe(start_x, start_y, end_x, end_y, duration)
            self.logger.debug(f"Swiped from ({start_x}, {start_y}) to ({end_x}, {end_y})")
        except Exception as e:
            self.logger.error(f"Failed to swipe: {e}")
            raise

    def scroll_to_element(
        self,
        locator: Tuple[str, str],
        max_swipes: int = 5
    ) -> Optional[Any]:
        for attempt in range(max_swipes):
            try:
                if self.is_element_visible(locator, timeout=2):
                    return self.find_element(locator)
                
                # Perform scroll
                size = self.driver.get_window_size()
                start_x = size["width"] // 2
                start_y = int(size["height"] * 0.8)
                end_y = int(size["height"] * 0.2)
                
                self.swipe(start_x, start_y, start_x, end_y, duration=800)
                
            except Exception as e:
                self.logger.warning(f"Scroll attempt {attempt + 1} failed: {e}")
        
        self.logger.warning(f"Element not found after {max_swipes} scrolls: {locator}")
        return None
    

    def wait_for_text_present(
        self,
        locator: Tuple[str, str],
        text: str,
        timeout: Optional[int] = None
    ) -> bool:

        try:
            self.wait_helper.wait_for_text_present(locator, text, timeout)
            return True
        except TimeoutException:
            return False

    def wait_for_element_to_disappear(
        self,
        locator: Tuple[str, str],
        timeout: Optional[int] = None
    ) -> bool:

        try:
            self.wait_helper.wait_for_element_invisible(locator, timeout)
            return True
        except TimeoutException:
            return False
