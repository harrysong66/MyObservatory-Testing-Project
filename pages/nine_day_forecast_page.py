"""9-Day Forecast page object for MyObservatory app."""

import re
from typing import Dict, List, Optional, Tuple

from appium.webdriver.common.appiumby import AppiumBy

from pages.base_page import BasePage
from utils import get_logger

logger = get_logger(__name__)


class NineDayForecastPage(BasePage):
    """Page object for 9-Day Forecast page."""

    # ============================================
    # LOCATORS
    # ============================================

    # Android locators
    ANDROID_LOCATORS = {
        "page_title": (
            AppiumBy.XPATH,
            '//android.widget.TextView[@text="9-Day Forecast"]'
        ),
        "forecast_container": (
            AppiumBy.ID,
            "hko.MyObservatory_v1_0:id/forecast_container"
        ),
        "forecast_items": (
            AppiumBy.ID,
            "hko.MyObservatory_v1_0:id/forecast_item"
        ),
        "date_text": (
            AppiumBy.ID,
            "hko.MyObservatory_v1_0:id/date_text"
        ),
        "weather_icon": (
            AppiumBy.ID,
            "hko.MyObservatory_v1_0:id/weather_icon"
        ),
        "temperature_text": (
            AppiumBy.ID,
            "hko.MyObservatory_v1_0:id/temperature"
        ),
        "humidity_text": (
            AppiumBy.ID,
            "hko.MyObservatory_v1_0:id/humidity"
        ),
    }

    # iOS locators
    IOS_LOCATORS = {
        "page_title": (
            AppiumBy.XPATH,
            '//XCUIElementTypeStaticText[@name="9-Day Forecast"]'
        ),
        "forecast_container": (
            AppiumBy.ACCESSIBILITY_ID,
            "forecast_container"
        ),
        "forecast_items": (
            AppiumBy.CLASS_NAME,
            "XCUIElementTypeCell"
        ),
        "date_text": (
            AppiumBy.ACCESSIBILITY_ID,
            "date_text"
        ),
        "weather_icon": (
            AppiumBy.ACCESSIBILITY_ID,
            "weather_icon"
        ),
        "temperature_text": (
            AppiumBy.ACCESSIBILITY_ID,
            "temperature"
        ),
        "humidity_text": (
            AppiumBy.ACCESSIBILITY_ID,
            "humidity"
        ),
        "back_button": (
            AppiumBy.ACCESSIBILITY_ID,
            "back"
        ),
    }

    def __init__(self, driver):
        """Initialize 9-Day Forecast page.
        
        Args:
            driver: Appium WebDriver instance
        """
        super().__init__(driver)
        self.platform = driver.capabilities.get("platformName", "Android").lower()
        self.locators = (
            self.ANDROID_LOCATORS if self.platform == "android" else self.IOS_LOCATORS
        )
        logger.info(f"NineDayForecastPage initialized for platform: {self.platform}")

    # ============================================
    # PAGE METHODS
    # ============================================

    def is_page_displayed(self, timeout: int = 10) -> bool:
        """Verify 9-Day Forecast page is displayed.
        
        Args:
            timeout: Maximum wait time
            
        Returns:
            True if page displayed, False otherwise
        """
        logger.debug("Checking if 9-Day Forecast page is displayed")
        
        is_displayed = (
            self.is_element_visible(self.locators["page_title"], timeout) or
            self.is_element_present(self.locators["forecast_container"], timeout)
        )
        
        if is_displayed:
            logger.info("9-Day Forecast page is displayed")
        else:
            logger.warning("9-Day Forecast page is not displayed")
        
        return is_displayed

    def wait_for_page_load(self, timeout: int = 20) -> bool:
        """Wait for 9-Day Forecast page to fully load.
        
        Args:
            timeout: Maximum wait time
            
        Returns:
            True if loaded, False otherwise
        """
        logger.info("Waiting for 9-Day Forecast page to load...")
        
        try:
            # Wait for page title or forecast items
            self.find_element(self.locators["page_title"], timeout, raise_exception=False)
            
            # Wait for forecast items to be present
            forecast_items = self.find_elements(self.locators["forecast_items"], timeout)
            
            if len(forecast_items) > 0:
                logger.info(f"9-Day Forecast page loaded with {len(forecast_items)} forecast items")
                return True
            else:
                logger.warning("9-Day Forecast page loaded but no forecast items found")
                return False
                
        except Exception as e:
            logger.error(f"9-Day Forecast page failed to load: {e}")
            return False

    def get_all_forecast_items(self) -> List:
        """Get all forecast item elements.
        
        Returns:
            List of forecast item WebElements
        """
        logger.info("Getting all forecast items")
        
        # Try to find forecast items
        forecast_items = self.find_elements(self.locators["forecast_items"], timeout=10)
        
        if not forecast_items:
            logger.warning("No forecast items found, trying alternative method")
            # Fallback: Try to get all text elements on page
            try:
                if self.platform == "android":
                    forecast_items = self.find_elements(
                        (AppiumBy.CLASS_NAME, "android.widget.LinearLayout"),
                        timeout=10
                    )
                else:
                    forecast_items = self.find_elements(
                        (AppiumBy.CLASS_NAME, "XCUIElementTypeCell"),
                        timeout=10
                    )
            except Exception as e:
                logger.error(f"Fallback method also failed: {e}")
                return []
        
        logger.info(f"Found {len(forecast_items)} forecast items")
        return forecast_items

    def get_forecast_by_day_offset(self, day_offset: int = 0) -> Optional[Dict[str, str]]:
        """Get forecast data for specific day by offset.
        
        Args:
            day_offset: Number of days from today (0=today, 1=tomorrow, 2=day after tomorrow)
            
        Returns:
            Dictionary with forecast data or None if not found
        """
        logger.info(f"Getting forecast for day offset: {day_offset}")
        
        try:
            forecast_items = self.get_all_forecast_items()
            
            if day_offset >= len(forecast_items):
                logger.error(f"Day offset {day_offset} exceeds available forecasts")
                return None
            
            item = forecast_items[day_offset]
            
            # Extract data from the forecast item
            forecast_data = self._extract_forecast_data(item)
            
            logger.info(f"Forecast data for day {day_offset}: {forecast_data}")
            return forecast_data
            
        except Exception as e:
            logger.error(f"Failed to get forecast by day offset: {e}")
            return None

    def _extract_forecast_data(self, element) -> Dict[str, str]:
        """Extract forecast data from element.
        
        Args:
            element: Forecast item WebElement
            
        Returns:
            Dictionary with extracted forecast data
        """
        try:
            # Get all text from the element
            element_text = element.text
            logger.debug(f"Element text: {element_text}")
            
            forecast_data = {
                "date": "",
                "temperature": "",
                "humidity": "",
                "raw_text": element_text
            }
            
            # Parse the text for different data
            lines = element_text.split("\n")
            
            for line in lines:
                line = line.strip()
                
                # Extract date
                if not forecast_data["date"] and any(day in line for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]):
                    forecast_data["date"] = line
                
                # Extract temperature (pattern: 20-25°C or 20°C - 25°C)
                temp_match = re.search(r'(\d+)\s*[-–]\s*(\d+)\s*°?[CF]?', line)
                if temp_match and not forecast_data["temperature"]:
                    forecast_data["temperature"] = f"{temp_match.group(1)}-{temp_match.group(2)}°C"
                
                # Extract humidity (pattern: 60-85% or 60%-85%)
                humidity_match = re.search(r'(\d+)\s*%?\s*[-–]\s*(\d+)\s*%', line)
                if humidity_match and not forecast_data["humidity"]:
                    forecast_data["humidity"] = f"{humidity_match.group(1)}-{humidity_match.group(2)}%"
            
            return forecast_data
            
        except Exception as e:
            logger.error(f"Failed to extract forecast data: {e}")
            return {"raw_text": str(element.text) if hasattr(element, "text") else ""}

    def extract_humidity_from_text(self, text: str) -> Optional[str]:
        """Extract humidity value from text.
        
        Args:
            text: Text containing humidity information
            
        Returns:
            Humidity string (e.g., "60-85%") or None
        """
        # Pattern to match humidity: 60-85%, 60%-85%, 60 - 85%
        humidity_pattern = r'(\d+)\s*%?\s*[-–]\s*(\d+)\s*%'
        
        match = re.search(humidity_pattern, text)
        if match:
            humidity = f"{match.group(1)}-{match.group(2)}%"
            logger.info(f"Extracted humidity: {humidity}")
            return humidity
        
        logger.warning(f"No humidity found in text: {text}")
        return None

    def get_day_after_tomorrow_humidity(self) -> Optional[str]:
        """Get humidity for the day after tomorrow (offset = 2).
        
        Returns:
            Humidity string or None if not found
        """
        logger.info("Getting humidity for day after tomorrow")
        
        forecast = self.get_forecast_by_day_offset(day_offset=2)
        
        if forecast and forecast.get("humidity"):
            logger.info(f"Day after tomorrow humidity: {forecast['humidity']}")
            return forecast["humidity"]
        
        # Fallback: Try to extract from raw text
        if forecast and forecast.get("raw_text"):
            humidity = self.extract_humidity_from_text(forecast["raw_text"])
            if humidity:
                return humidity
        
        logger.error("Failed to get day after tomorrow humidity")
        return None