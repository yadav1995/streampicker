import time
from app.services.cache_service import SimpleCache

def test_cache_set_get_hit():
    c = SimpleCache(default_ttl=10)
    c.set("key1", {"title": "Inception"})
    val = c.get("key1")
    assert val == {"title": "Inception"}
    stats = c.get_stats()
    assert stats["hits"] == 1
    assert stats["misses"] == 0

def test_cache_ttl_expiration():
    c = SimpleCache(default_ttl=1)
    c.set("exp_key", "hello", ttl=1)
    assert c.get("exp_key") == "hello"
    time.sleep(1.1)
    assert c.get("exp_key") is None
    stats = c.get_stats()
    assert stats["evictions"] >= 1

def test_cache_clear_prefix():
    c = SimpleCache()
    c.set("pick:user1", "val1")
    c.set("pick:user2", "val2")
    c.set("roi:user1", "val3")
    deleted = c.clear_prefix("pick:")
    assert deleted == 2
    assert c.get("pick:user1") is None
    assert c.get("roi:user1") == "val3"
