from datetime import datetime

import pytest
import requests

from src.live_weather import (
    fetch_current_weather,
    load_weather_snapshot,
    save_weather_snapshot,
    weather_description,
)


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self, payload):
        self.payload = payload
        self.request = None

    def get(self, url, *, params, timeout):
        self.request = (url, params, timeout)
        return FakeResponse(self.payload)


def test_fetch_current_weather_returns_observed_conditions():
    session = FakeSession(
        {
            "current": {
                "time": "2026-11-12T10:00",
                "temperature_2m": 12.5,
                "relative_humidity_2m": 61,
                "weather_code": 61,
                "wind_speed_10m": 18.0,
            }
        }
    )

    weather = fetch_current_weather(session)

    assert weather == {
        "observed_at": datetime(2026, 11, 12, 10, 0),
        "temperature_c": 12.5,
        "relative_humidity_percent": 61,
        "weather_code": 61,
        "wind_speed_kmh": 18.0,
    }
    assert session.request[1]["timezone"] == "America/New_York"
    assert session.request[2] == (5, 15)


def test_fetch_current_weather_rejects_missing_observation():
    with pytest.raises(ValueError, match="did not contain current conditions"):
        fetch_current_weather(FakeSession({"current": {}}))


def test_fetch_current_weather_surfaces_http_failures():
    class FailedResponse(FakeResponse):
        def raise_for_status(self):
            raise requests.HTTPError("service unavailable")

    class FailedSession(FakeSession):
        def get(self, url, *, params, timeout):
            return FailedResponse({})

    with pytest.raises(requests.HTTPError, match="service unavailable"):
        fetch_current_weather(FailedSession({}))


def test_weather_snapshot_round_trips_and_avoids_unchanged_writes(tmp_path):
    path = tmp_path / "live_weather.json"
    weather = {
        "observed_at": datetime(2026, 11, 12, 10, 0),
        "temperature_c": 12.5,
        "relative_humidity_percent": 61,
        "weather_code": 61,
        "wind_speed_kmh": 18.0,
    }

    assert save_weather_snapshot(weather, path)
    assert load_weather_snapshot(path) == weather
    assert not save_weather_snapshot(weather, path)


def test_load_weather_snapshot_reports_missing_snapshot(tmp_path):
    with pytest.raises(ValueError, match="missing or invalid"):
        load_weather_snapshot(tmp_path / "missing.json")


@pytest.mark.parametrize(
    ("code", "description"),
    [
        (0, "Clear sky"),
        (1, "Mainly clear"),
        (2, "Partly cloudy"),
        (3, "Overcast"),
        (61, "Rain"),
        (95, "Thunderstorm"),
    ],
)
def test_weather_description_maps_common_weather_codes(code, description):
    assert weather_description(code) == description
