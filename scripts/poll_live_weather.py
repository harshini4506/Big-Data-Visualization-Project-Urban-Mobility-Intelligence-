from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.live_weather import fetch_current_weather, save_weather_snapshot


def main() -> None:
    weather = fetch_current_weather()
    changed = save_weather_snapshot(weather)
    if changed:
        print(f"Saved new weather observation from {weather['observed_at']}.")
    else:
        print(f"No new observation; keeping {weather['observed_at']}.")


if __name__ == "__main__":
    main()
