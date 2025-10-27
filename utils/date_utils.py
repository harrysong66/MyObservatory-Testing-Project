"""Date and time utility functions."""

from datetime import datetime, timedelta
from typing import Optional


def get_today() -> datetime:
    return datetime.now()


def get_day_after_tomorrow() -> datetime:
    return datetime.now() + timedelta(days=2)


def get_date_offset(days: int) -> datetime:
    return datetime.now() + timedelta(days=days)


def format_date(date: datetime, format_str: str = "%Y-%m-%d") -> str:
    return date.strftime(format_str)


def get_weekday_name(date: Optional[datetime] = None) -> str:
    if date is None:
        date = datetime.now()
    return date.strftime("%A")


def parse_date(date_str: str, format_str: str = "%Y-%m-%d") -> datetime:
    return datetime.strptime(date_str, format_str)


def is_same_day(date1: datetime, date2: datetime) -> bool:
    return date1.date() == date2.date()


def get_days_between(date1: datetime, date2: datetime) -> int:
    return abs((date2.date() - date1.date()).days)