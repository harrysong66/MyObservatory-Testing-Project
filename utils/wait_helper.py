"""Wait utilities for handling element synchronization."""

from typing import Any, Callable, Optional

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.logger import get_logger

logger = get_logger(__name__)


class WaitHelper:
    """Helper class for waiting operations."""

    def __init__(self, driver: Any, timeout: int = 20, poll_frequency: float = 0.5):
        self.driver = driver
        self.timeout = timeout
        self.poll_frequency = poll_frequency
        self.wait = WebDriverWait(driver, timeout, poll_frequency)

    def wait_for_element_visible(self, locator: tuple, timeout: Optional[int] = None) -> Any:
        wait_time = timeout or self.timeout
        wait = WebDriverWait(self.driver, wait_time, self.poll_frequency)
        
        try:
            logger.debug(f"Waiting for element to be visible: {locator}")
            element = wait.until(EC.visibility_of_element_located(locator))
            logger.debug(f"Element found: {locator}")
            return element
        except TimeoutException:
            logger.error(f"Element not visible after {wait_time}s: {locator}")
            raise

    def wait_for_element_present(self, locator: tuple, timeout: Optional[int] = None) -> Any:
        wait_time = timeout or self.timeout
        wait = WebDriverWait(self.driver, wait_time, self.poll_frequency)
        
        try:
            logger.debug(f"Waiting for element to be present: {locator}")
            element = wait.until(EC.presence_of_element_located(locator))
            logger.debug(f"Element present: {locator}")
            return element
        except TimeoutException:
            logger.error(f"Element not present after {wait_time}s: {locator}")
            raise

    def wait_for_element_clickable(self, locator: tuple, timeout: Optional[int] = None) -> Any:
        wait_time = timeout or self.timeout
        wait = WebDriverWait(self.driver, wait_time, self.poll_frequency)
        
        try:
            logger.debug(f"Waiting for element to be clickable: {locator}")
            element = wait.until(EC.element_to_be_clickable(locator))
            logger.debug(f"Element clickable: {locator}")
            return element
        except TimeoutException:
            logger.error(f"Element not clickable after {wait_time}s: {locator}")
            raise

    def wait_for_elements_present(self, locator: tuple, timeout: Optional[int] = None) -> list:
        wait_time = timeout or self.timeout
        wait = WebDriverWait(self.driver, wait_time, self.poll_frequency)
        
        try:
            logger.debug(f"Waiting for elements to be present: {locator}")
            elements = wait.until(EC.presence_of_all_elements_located(locator))
            logger.debug(f"Found {len(elements)} elements: {locator}")
            return elements
        except TimeoutException:
            logger.error(f"Elements not present after {wait_time}s: {locator}")
            raise

    def wait_for_element_invisible(self, locator: tuple, timeout: Optional[int] = None) -> bool:

        wait_time = timeout or self.timeout
        wait = WebDriverWait(self.driver, wait_time, self.poll_frequency)
        
        try:
            logger.debug(f"Waiting for element to be invisible: {locator}")
            result = wait.until(EC.invisibility_of_element_located(locator))
            logger.debug(f"Element invisible: {locator}")
            return result
        except TimeoutException:
            logger.error(f"Element still visible after {wait_time}s: {locator}")
            raise

    def wait_for_condition(
        self,
        condition: Callable,
        timeout: Optional[int] = None,
        error_message: str = "Condition not met"
    ) -> Any:
        wait_time = timeout or self.timeout
        wait = WebDriverWait(self.driver, wait_time, self.poll_frequency)
        
        try:
            logger.debug(f"Waiting for custom condition: {error_message}")
            result = wait.until(condition)
            logger.debug(f"Condition met: {error_message}")
            return result
        except TimeoutException:
            logger.error(f"{error_message} after {wait_time}s")
            raise TimeoutException(error_message)

    def wait_for_text_present(
        self,
        locator: tuple,
        text: str,
        timeout: Optional[int] = None
    ) -> bool:
        wait_time = timeout or self.timeout
        wait = WebDriverWait(self.driver, wait_time, self.poll_frequency)
        
        try:
            logger.debug(f"Waiting for text '{text}' in element: {locator}")
            result = wait.until(EC.text_to_be_present_in_element(locator, text))
            logger.debug(f"Text '{text}' found in element: {locator}")
            return result
        except TimeoutException:
            logger.error(f"Text '{text}' not present after {wait_time}s: {locator}")
            raise
