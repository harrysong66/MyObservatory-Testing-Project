"""Pages package initialization."""

from .base_page import BasePage
from .navigation_drawer_page import NavigationDrawerPage
from .home_page import HomePage
from .nine_day_forecast_page import NineDayForecastPage
from .slide_page import SlidePage
from .agreement_page import AgreementPage

__all__ = [
    "BasePage",
    "HomePage",
    "NavigationDrawerPage",
    "NineDayForecastPage",
    "SlidePage",
    "NineDayForecastPage",
    "AgreementPage",
]
