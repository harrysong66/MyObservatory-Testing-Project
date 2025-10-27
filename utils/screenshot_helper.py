"""Screenshot utility for capturing screenshots on failures."""

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from utils.logger import get_logger

logger = get_logger(__name__)


class ScreenshotHelper:
    """Helper class for capturing and managing screenshots."""

    def __init__(self, driver: Any, screenshot_dir: str = "reports/screenshots"):
        self.driver = driver
        self.screenshot_dir = Path(screenshot_dir)
        self._ensure_screenshot_dir()

    def _ensure_screenshot_dir(self) -> None:
        """Ensure screenshot directory exists."""
        try:
            self.screenshot_dir.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Screenshot directory ready: {self.screenshot_dir}")
        except Exception as e:
            logger.error(f"Failed to create screenshot directory: {e}")

    def capture_screenshot(self, filename: Optional[str] = None) -> Optional[str]:
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                filename = f"screenshot_{timestamp}"
            
            # Ensure .png extension
            if not filename.endswith(".png"):
                filename = f"{filename}.png"
            
            filepath = self.screenshot_dir / filename
            
            # Capture screenshot
            self.driver.save_screenshot(str(filepath))
            logger.info(f"Screenshot saved: {filepath}")
            
            return str(filepath)
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            return None

    def capture_screenshot_on_failure(self, test_name: str) -> Optional[str]:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_test_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in test_name)
        filename = f"FAILED_{safe_test_name}_{timestamp}.png"
        
        return self.capture_screenshot(filename)

    def capture_element_screenshot(
        self,
        element: Any,
        filename: Optional[str] = None
    ) -> Optional[str]:
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                filename = f"element_{timestamp}"
            
            if not filename.endswith(".png"):
                filename = f"{filename}.png"
            
            filepath = self.screenshot_dir / filename
            
            # Capture element screenshot
            element.screenshot(str(filepath))
            logger.info(f"Element screenshot saved: {filepath}")
            
            return str(filepath)
        except Exception as e:
            logger.error(f"Failed to capture element screenshot: {e}")
            return None

    def cleanup_old_screenshots(self, days: int = 7) -> None:
        try:
            cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
            
            for filepath in self.screenshot_dir.glob("*.png"):
                if filepath.stat().st_mtime < cutoff_time:
                    filepath.unlink()
                    logger.debug(f"Deleted old screenshot: {filepath}")
            
            logger.info(f"Cleaned up screenshots older than {days} days")
        except Exception as e:
            logger.error(f"Failed to cleanup screenshots: {e}")


def get_screenshot_helper(driver: Any) -> ScreenshotHelper:
    screenshot_dir = os.getenv("SCREENSHOT_DIR", "reports/screenshots")
    return ScreenshotHelper(driver, screenshot_dir)
