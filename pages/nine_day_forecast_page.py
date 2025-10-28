import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from appium.webdriver.common.appiumby import AppiumBy

from pages.base_page import BasePage
from utils import get_logger

logger = get_logger(__name__)


class NineDayForecastPage(BasePage):

    # Android locators
    ANDROID_LOCATORS = {
        "roll_box": (
            AppiumBy.XPATH,
            '//*[@resource-id="hko.MyObservatory_v1_0:id/mainAppSevenDayView"]/android.widget.LinearLayout'
            )
    }

    # iOS locators
    IOS_LOCATORS = {
    }

    def __init__(self, driver):
        super().__init__(driver)
        self.platform = driver.capabilities.get("platformName", "Android").lower()
        self.locators = (
            self.ANDROID_LOCATORS if self.platform == "android" else self.IOS_LOCATORS
        )
        logger.info(f"NineDayForecastPage initialized for platform: {self.platform}")


    def get_day_forecast(self, day):
        
        target_dt = datetime.now() + timedelta(days=day)
        target_date = f"{target_dt.day} {target_dt.strftime('%b')}"
        day_forecast = self.find_element((AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiScrollable(new UiSelector().scrollable(true))'
            f'.scrollIntoView(new UiSelector().descriptionContains("{target_date}"))')
        )
        return day_forecast
    
    def is_page_displayed(self, timeout: int = 10) -> bool:
        logger.debug("checking if 9 Day Forecast page is displayed")
        
        is_displayed = self.is_element_visible(self.locators["roll_box"], timeout)
        
        if is_displayed:
            logger.info("9 day page is displayed")
        else:
            logger.warning("9 day page is not displayed")
        
        return is_displayed