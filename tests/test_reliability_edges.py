"""Regression checks for repeated setup and shutdown probe isolation."""

import signal

from app.lifecycle import Lifecycle


def test_repeated_install_preserves_original_handler(monkeypatch):
    calls = []
    original = lambda signum, frame: calls.append(signum)
    handlers = {signal.SIGTERM: original, signal.SIGINT: original}
    monkeypatch.setattr(signal, "getsignal", handlers.get)
    monkeypatch.setattr(signal, "signal", lambda sig, handler: handlers.update({sig: handler}))
    life = Lifecycle()
    life.install()
    life.install()
    life.request_shutdown(signal.SIGTERM, None)
    assert life.shutting_down
    assert calls == [signal.SIGTERM]


def test_shutdown_readiness_does_not_ping_redis(client_factory):
    from app.lifecycle import lifecycle

    class UnreachableStore:
        def ping(self):
            raise AssertionError("Shutdown readiness must not contact Redis")

    client = client_factory(store=UnreachableStore())
    lifecycle.shutting_down = True
    response = client.get("/ready")
    assert response.status_code == 503
    assert response.json() == {"status": "shutting_down"}
