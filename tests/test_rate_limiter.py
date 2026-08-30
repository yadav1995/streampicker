from app.services.rate_limiter import TokenBucketRateLimiter

def test_rate_limiter_allows_under_quota():
    limiter = TokenBucketRateLimiter(requests_per_minute=60, burst_limit=5)
    allowed1, rem1, reset1 = limiter.is_allowed("test_ip")
    assert allowed1 is True
    assert rem1 == 4

def test_rate_limiter_blocks_on_burst_exceeded():
    limiter = TokenBucketRateLimiter(requests_per_minute=60, burst_limit=2)
    allowed1, _, _ = limiter.is_allowed("client_a")
    allowed2, _, _ = limiter.is_allowed("client_a")
    allowed3, _, _ = limiter.is_allowed("client_a")
    
    assert allowed1 is True
    assert allowed2 is True
    assert allowed3 is False
