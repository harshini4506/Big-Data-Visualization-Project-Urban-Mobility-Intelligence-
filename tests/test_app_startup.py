from pathlib import Path

from streamlit.testing.v1 import AppTest

from src import bootstrap, config


def test_app_loads_data_on_request_and_offers_retry_on_failure(tmp_path, monkeypatch):
    calls = []

    def fail_to_load_data():
        calls.append(True)
        raise RuntimeError("TLC download unavailable")

    monkeypatch.setattr(config, "PROCESSED_DIR", tmp_path)
    monkeypatch.setattr(bootstrap, "bootstrap_data", fail_to_load_data)

    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py").run(timeout=120)

    assert not app.exception
    assert not calls
    assert [button.label for button in app.button] == ["Load January 2025 data"]

    app.button[0].click().run(timeout=120)
    assert len(calls) == 1
    assert any("Could not load NYC TLC trip data" in item.value for item in app.error)
    assert [button.label for button in app.button] == ["Retry loading data"]

    app.button[0].click().run(timeout=120)
    assert len(calls) == 2
