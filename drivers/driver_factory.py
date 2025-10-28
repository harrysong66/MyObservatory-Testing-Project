from typing import Any, Optional

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions

from config import config
from utils.logger import get_logger

logger = get_logger(__name__)


class AppiumDriverFactory:
    """Factory for creating Appium WebDriver instances with proper configuration."""

    @staticmethod
    def create_driver(
        platform: Optional[str] = None,
        capabilities: Optional[dict] = None
    ) -> webdriver.Remote:
        platform = (platform or config.test.platform).lower()
        appium_url = config.get_appium_url()
        
        logger.info(f"Creating Appium driver for platform: {platform}")
        logger.info(f"Appium server URL: {appium_url}")
        
        try:
            if platform == "android":
                return AppiumDriverFactory._create_android_driver(appium_url, capabilities)
            elif platform == "ios":
                return AppiumDriverFactory._create_ios_driver(appium_url, capabilities)
            else:
                raise ValueError(f"Unsupported platform: {platform}")
        except Exception as e:
            logger.error(f"Failed to create driver: {e}")
            raise

    @staticmethod
    def _create_android_driver(
        appium_url: str,
        capabilities: Optional[dict] = None
    ) -> webdriver.Remote:
        caps = capabilities or config.get_capabilities("android")
        logger.debug(f"Android capabilities: {caps}")
        
        try:
            # Use UiAutomator2Options for better type safety
            options = UiAutomator2Options()
            options.load_capabilities(caps)
            
            driver = webdriver.Remote(
                command_executor=appium_url,
                options=options
            )
            
            # Set implicit wait
            driver.implicitly_wait(config.test.implicit_wait)
            
            logger.info("Android driver created successfully")
            return driver
            
        except Exception as e:
            logger.error(f"Failed to create Android driver: {e}")
            logger.info("Attempting fallback configuration...")
            
            # Fallback: Try with basic capabilities
            try:
                options = UiAutomator2Options()
                options.platform_name = "Android"
                options.automation_name = "UiAutomator2"
                options.device_name = caps.get("deviceName", "Android Device")
                
                if "appPackage" in caps:
                    options.app_package = caps["appPackage"]
                if "appActivity" in caps:
                    options.app_activity = caps["appActivity"]
                
                driver = webdriver.Remote(
                    command_executor=appium_url,
                    options=options
                )
                driver.implicitly_wait(config.test.implicit_wait)
                
                logger.info("Android driver created with fallback configuration")
                return driver
            except Exception as fallback_error:
                logger.error(f"Fallback also failed: {fallback_error}")
                raise

    @staticmethod
    def _create_ios_driver(
        appium_url: str,
        capabilities: Optional[dict] = None
    ) -> webdriver.Remote:
        caps = capabilities or config.get_capabilities("ios")
        logger.debug(f"iOS capabilities: {caps}")
        
        try:
            # Use XCUITestOptions for better type safety
            options = XCUITestOptions()
            options.load_capabilities(caps)
            
            driver = webdriver.Remote(
                command_executor=appium_url,
                options=options
            )
            
            # Set implicit wait
            driver.implicitly_wait(config.test.implicit_wait)
            
            logger.info("iOS driver created successfully")
            return driver
            
        except Exception as e:
            logger.error(f"Failed to create iOS driver: {e}")
            logger.info("Attempting fallback configuration...")
            
            # Fallback: Try with basic capabilities
            try:
                options = XCUITestOptions()
                options.platform_name = "iOS"
                options.automation_name = "XCUITest"
                options.device_name = caps.get("deviceName", "iPhone 14")
                
                if "bundleId" in caps:
                    options.bundle_id = caps["bundleId"]
                
                driver = webdriver.Remote(
                    command_executor=appium_url,
                    options=options
                )
                driver.implicitly_wait(config.test.implicit_wait)
                
                logger.info("iOS driver created with fallback configuration")
                return driver
            except Exception as fallback_error:
                logger.error(f"Fallback also failed: {fallback_error}")
                raise

    @staticmethod
    def quit_driver(driver: Optional[Any]) -> None:
        if driver:
            try:
                logger.info(f"Quitting {config.test.platform} driver...")
                driver.quit()
                logger.info(f"{config.test.platform} Driver quit successfully")
            except Exception as e:
                logger.error(f"Error quitting {config.test.platform} driver: {e}")


# Convenience function
def create_driver(platform: Optional[str] = None) -> webdriver.Remote:
    return AppiumDriverFactory.create_driver(platform)

def quit_driver(driver: Optional[Any]) -> None:
    AppiumDriverFactory.quit_driver(driver)
