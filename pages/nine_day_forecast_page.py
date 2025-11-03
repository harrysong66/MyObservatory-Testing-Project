from typing import List, Optional
from datetime import datetime, timedelta
from pathlib import Path
from appium.webdriver.common.appiumby import AppiumBy

from pages.base_page import BasePage
from utils import get_logger
from utils.screenshot_helper import get_screenshot_helper

logger = get_logger(__name__)


class NineDayForecastPage(BasePage):

    # Android locators
    ANDROID_LOCATORS = {
        "roll_box": (
            AppiumBy.XPATH,
            '//*[@resource-id="hko.MyObservatory_v1_0:id/mainAppSevenDayView"]/android.widget.LinearLayout'
            )
        ,
        # 9-day list container (ListView)
        "list_view": (
            AppiumBy.ID,
            'hko.MyObservatory_v1_0:id/mainAppSevenDayView'
        ),
        # Date label within each day item
        "date_label": (
            AppiumBy.ID,
            'hko.MyObservatory_v1_0:id/sevenday_forecast_date'
        ),
        # Top tabs
        "tab_nine_day": (
            AppiumBy.XPATH,
            "//android.widget.LinearLayout[@content-desc='9-Day Forecast']"
        ),
        "tab_nine_day_text": (
            AppiumBy.XPATH,
            "//android.widget.TextView[@text='9-Day Forecast']"
        ),
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


    def ensure_on_nine_day_tab(self, timeout: int = 10) -> None:
        tab_locator = self.locators.get("tab_nine_day") or self.locators.get("tab_nine_day_text")
        if not tab_locator:
            return
        tab_el = self.find_element(tab_locator, timeout=timeout, raise_exception=False)
        if tab_el:
            try:
                selected = str(tab_el.get_attribute("selected")).lower() == "true"
            except Exception:
                selected = False
            if not selected:
                self.logger.info("Selecting '9-Day Forecast' tab")
                self.click(tab_locator, timeout=timeout, wait_for_clickable=True)

    def get_day_forecast(self, day):

        # Make sure we are on the correct tab to avoid landing on 'Extended Outlook'
        self.ensure_on_nine_day_tab(timeout=8)
        index = int(day)
        
        def ascend_to_item(element) -> Optional[object]:
            try:
                current = element
                for _ in range(6):
                    # If this node has a contentDescription, it should be the item container
                    try:
                        cd = current.get_attribute("contentDescription")
                        if cd:
                            return current
                    except Exception:
                        pass
                    parent = current.find_element(AppiumBy.XPATH, "..")
                    if not parent or parent.get_attribute("className") == "android.widget.ListView":
                        return current
                    current = parent
            except Exception:
                return element
            return element
        
        # As a last resort, try date-fragment search with vertical scroll
        target_dt = datetime.now() + timedelta(days=index)
        day_no_zero = str(target_dt.day)
        day_zero = f"{target_dt.day:02d}"
        month_abbr = target_dt.strftime('%b')
        month_full = target_dt.strftime('%B')

        for frag in (f"{day_no_zero} {month_abbr}", f"{day_zero} {month_abbr}", f"{day_no_zero} {month_full}", f"{day_zero} {month_full}"):
            try:
                expr = (
                    'new UiScrollable(new UiSelector().resourceId("hko.MyObservatory_v1_0:id/mainAppSevenDayView")).'
                    f'scrollIntoView(new UiSelector().textContains("{frag}"))'
                )
                el = self.find_element((AppiumBy.ANDROID_UIAUTOMATOR, expr), timeout=3, raise_exception=False)
                if el:
                    return ascend_to_item(el)
            except Exception:
                pass

        # Diagnostics and raise
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ps_dir = Path("reports/page_source")
            ps_dir.mkdir(parents=True, exist_ok=True)
            ps_path = ps_dir / f"nine_day_page_source_{timestamp}.xml"
            with open(ps_path, "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            self.logger.info(f"Saved 9-day page source to: {ps_path}")
            sh = get_screenshot_helper(self.driver)
            sh.capture_screenshot(f"nine_day_forecast_not_found_{timestamp}.png")
        except Exception as diag_err:
            self.logger.error(f"Failed to capture 9-day diagnostics: {diag_err}")

        raise TimeoutError(f"Could not find the forecast item for day index {index}")
    
    def is_page_displayed(self, timeout: int = 10) -> bool:
        logger.debug("checking if 9 Day Forecast page is displayed")

        # Ensure the correct tab is selected
        self.ensure_on_nine_day_tab(timeout=5)

        # Consider displayed if either the roll_box appears or the tab shows selected=true
        try:
            if self.is_element_visible(self.locators["roll_box"], timeout):
                logger.info("9 day page is displayed (roll_box visible)")
                return True
        except Exception:
            pass

        tab_locator = self.locators.get("tab_nine_day") or self.locators.get("tab_nine_day_text")
        if tab_locator:
            tab_el = self.find_element(tab_locator, timeout=3, raise_exception=False)
            if tab_el and str(tab_el.get_attribute("selected")).lower() == "true":
                logger.info("9 day page is displayed (tab selected)")
                return True

        logger.warning("9 day page is not displayed")
        return False