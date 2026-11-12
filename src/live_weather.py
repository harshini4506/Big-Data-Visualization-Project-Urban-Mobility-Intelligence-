"""Current New York City weather context from Open-Meteo."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import requests

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
NEW_YORK_COORDINATES = (40.7128, -74.0060)
WEATHER_SNAPSHOT_PATH = Path(__file__).resolve().parents[1] / "data" / "live_weather.json"


def fetch_current_weather(
    session: requests.Session | None = None,
) -> dict[str, object]:
    client = session or requests
    response = client.get(
        OPEN_METEO_URL,
        params={
            "latitude": NEW_YORK_COORDINATES[0],
            "longitude": NEW_YORK_COORDINATES[1],
            "current": "temperature_2m,precipitation,weather_code,wind_speed_10m",
            "timezone": "America/New_York",
        },
        timeout=(5, 15),
    )
    response.raise_for_status()
    current = response.json().get("current")
    if not isinstance(current, dict) or not current.get("time"):
        raise ValueError("The weather response did not contain current conditions.")

    try:
        return {
            "observed_at": datetime.fromisoformat(current["time"]),
            "temperature_c": float(current["temperature_2m"]),
            "precipitation_mm": float(current["precipitation"]),
            "weather_code": int(current["weather_code"]),
            "wind_speed_kmh": float(current["wind_speed_10m"]),
        }
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("The weather response contained invalid current conditions.") from exc


def save_weather_snapshot(
    weather: dict[str, object],
    path: Path = WEATHER_SNAPSHOT_PATH,
) -> bool:
    snapshot = {
        "observed_at": weather["observed_at"].isoformat(),
        "temperature_c": weather["temperature_c"],
        "precipitation_mm": weather["precipitation_mm"],
        "weather_code": weather["weather_code"],
        "wind_speed_kmh": weather["wind_speed_kmh"],
    }
    content = json.dumps(snapshot, indent=2, sort_keys=True) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def load_weather_snapshot(path: Path = WEATHER_SNAPSHOT_PATH) -> dict[str, object]:
    try:
        snapshot = json.loads(path.read_text(encoding="utf-8"))
        return {
            "observed_at": datetime.fromisoformat(snapshot["observed_at"]),
            "temperature_c": float(snapshot["temperature_c"]),
            "precipitation_mm": float(snapshot["precipitation_mm"]),
            "weather_code": int(snapshot["weather_code"]),
            "wind_speed_kmh": float(snapshot["wind_speed_kmh"]),
        }
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise ValueError("The saved weather snapshot is missing or invalid.") from exc


def weather_description(code: int) -> str:
    if code == 0:
        return "Clear sky"
    if code == 1:
        return "Mainly clear"
    if code == 2:
        return "Partly cloudy"
    if code == 3:
        return "Overcast"
    if code in {45, 48}:
        return "Fog"
    if code in {51, 53, 55, 56, 57}:
        return "Drizzle"
    if code in {61, 63, 65, 66, 67, 80, 81, 82}:
        return "Rain"
    if code in {71, 73, 75, 77, 85, 86}:
        return "Snow"
    if code in {95, 96, 99}:
        return "Thunderstorm"
    return "Conditions unavailable"
