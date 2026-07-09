from datetime import datetime
from zoneinfo import ZoneInfo

from app.core.clock import local_today
from app.core.config import settings


def _freeze_at(monkeypatch, hour, minute=0):
    tz = ZoneInfo(settings.app_timezone)
    fixed = datetime(2026, 7, 9, hour, minute, tzinfo=tz)

    class FrozenDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return fixed if tz is None else fixed.astimezone(tz)

    monkeypatch.setattr("app.core.clock.datetime", FrozenDateTime)


def test_local_today_before_cutoff_is_still_previous_day(monkeypatch):
    _freeze_at(monkeypatch, 2, 30)
    assert local_today().isoformat() == "2026-07-08"


def test_local_today_one_minute_before_cutoff_is_still_previous_day(monkeypatch):
    _freeze_at(monkeypatch, 5, 59)
    assert local_today().isoformat() == "2026-07-08"


def test_local_today_exactly_at_cutoff_rolls_over(monkeypatch):
    _freeze_at(monkeypatch, 6, 0)
    assert local_today().isoformat() == "2026-07-09"


def test_local_today_one_minute_after_cutoff_is_current_day(monkeypatch):
    _freeze_at(monkeypatch, 6, 1)
    assert local_today().isoformat() == "2026-07-09"


def test_local_today_at_midday_is_current_day(monkeypatch):
    _freeze_at(monkeypatch, 12, 0)
    assert local_today().isoformat() == "2026-07-09"


def test_local_today_at_midnight_is_still_previous_day(monkeypatch):
    _freeze_at(monkeypatch, 0, 0)
    assert local_today().isoformat() == "2026-07-08"


def test_local_today_just_before_midnight_is_current_day(monkeypatch):
    _freeze_at(monkeypatch, 23, 59)
    assert local_today().isoformat() == "2026-07-09"
