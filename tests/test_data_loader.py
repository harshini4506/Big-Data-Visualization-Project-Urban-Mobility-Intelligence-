from src import data_loader


class FakeResponse:
    def __init__(self, status_code, chunks=()):
        self.status_code = status_code
        self.chunks = chunks

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def raise_for_status(self):
        if self.status_code >= 400 and self.status_code != 404:
            raise RuntimeError(f"HTTP {self.status_code}")

    def iter_content(self, chunk_size):
        yield from self.chunks


def test_download_processed_bundle_streams_to_destination(tmp_path, monkeypatch):
    destination = tmp_path / "urban-mobility-data.zip"
    monkeypatch.setattr(
        data_loader.requests,
        "get",
        lambda *args, **kwargs: FakeResponse(200, [b"bundle", b"-data"]),
    )

    assert data_loader.download_processed_bundle(2025, 1, destination)
    assert destination.read_bytes() == b"bundle-data"
    assert not destination.with_suffix(".part").exists()


def test_download_processed_bundle_returns_false_when_release_is_missing(tmp_path, monkeypatch):
    destination = tmp_path / "urban-mobility-data.zip"
    monkeypatch.setattr(
        data_loader.requests,
        "get",
        lambda *args, **kwargs: FakeResponse(404),
    )

    assert not data_loader.download_processed_bundle(2025, 1, destination)
    assert not destination.exists()
    assert not destination.with_suffix(".part").exists()
