"""Extra checks for concurrency, expiry, and blocking before LLM work."""

from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi import HTTPException

from app.cost_guard import CostGuard, KEY_TTL_SECONDS
from app.rate_limiter import RateLimiter, WINDOW_SECONDS


def test_concurrent_requests_do_not_exceed_quota(fake_redis):
    limiter = RateLimiter(fake_redis, 5)

    def attempt(_):
        try:
            limiter.check("concurrent", now=1000.0)
            return 200
        except HTTPException as error:
            assert error.headers["Retry-After"] == str(WINDOW_SECONDS)
            return error.status_code

    with ThreadPoolExecutor(max_workers=8) as pool:
        statuses = list(pool.map(attempt, range(24)))
    assert statuses.count(200) == 5
    assert statuses.count(429) == 19
    assert limiter.hit_count("concurrent", now=1000.0) == 5
    assert 0 < fake_redis.ttl(limiter._key("concurrent")) <= WINDOW_SECONDS


def test_cost_month_isolation_and_expiry(fake_redis):
    guard = CostGuard(fake_redis, 1.0)
    guard.record("monthly", 0.9, month="2026-09")
    guard.check("monthly", estimated_cost=0.5, month="2026-10")
    with pytest.raises(HTTPException) as error:
        guard.check("monthly", estimated_cost=0.5, month="2026-09")
    assert error.value.status_code == 402
    assert 0 < fake_redis.ttl(guard._key("monthly", "2026-09")) <= KEY_TTL_SECONDS


@pytest.mark.parametrize("blocked_status", [401, 429, 402])
def test_blocked_request_never_calls_llm(
    blocked_status, client_factory, fake_redis, auth_headers, monkeypatch
):
    from app import main

    def unexpected_call(*args, **kwargs):
        pytest.fail("Blocked request reached the LLM")

    monkeypatch.setattr(main, "ask_llm", unexpected_call)
    client = client_factory(rate_limit=0 if blocked_status == 429 else 10)
    if blocked_status == 402:
        fake_redis.set(CostGuard._key("sv-test"), "999")
    response = client.post(
        "/ask", json={"question": "Hello"},
        headers={} if blocked_status == 401 else auth_headers,
    )
    assert response.status_code == blocked_status
    if blocked_status == 401:
        assert not fake_redis.exists(RateLimiter._key("sv-test"))
