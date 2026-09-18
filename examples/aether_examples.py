"""Offline, individually labeled examples for every Aether feature."""

from godai import aether


@aether.timeout(1)
def bounded_call() -> str:
    return "fast"


@aether.debounce(60)
def debounced_call(value: int) -> int:
    return value


def main() -> None:
    # 1. aether.timeout - completes before its one-second deadline.
    print("1. aether.timeout:", bounded_call())

    # 2. aether.circuit_breaker - returns a successful provider result.
    breaker = aether.circuit_breaker("demo", threshold=2)
    print("2. aether.circuit_breaker:", breaker.call(lambda: "ok"))

    # 3. aether.offline_queue - stores a JSON payload in SQLite.
    pending = aether.offline_queue("/tmp/godai-queue.sqlite3")
    pending.put({"prompt": "retry"})
    print("3. aether.offline_queue:", pending.get_all())

    # 4. aether.heuristics - diagnoses a KeyError locally.
    print("4. aether.heuristics:", aether.heuristics(KeyError("x")))

    # 5. aether.fallback_provider - returns the first successful provider.
    print("5. aether.fallback_provider:", aether.fallback_provider([lambda: "first"]))

    # 6. aether.degraded_mode - checks connectivity and reports the mode.
    print("6. aether.degraded_mode:", aether.degraded_mode())

    # 7. aether.lazy_load - imports json only when requested.
    print("7. aether.lazy_load:", aether.lazy_load("json").__name__)

    # 8. aether.zero_overhead - measures a small decorated fast path.
    print("8. aether.zero_overhead:", aether.zero_overhead(100))

    # 9. aether.network_probe - probes a local closed port without external calls.
    print("9. aether.network_probe:", aether.network_probe("127.0.0.1", 9))

    # 10. aether.missing_dependency_helper - confirms a standard module is available.
    print("10. aether.missing_dependency_helper:", aether.missing_dependency_helper("json"))

    # 11. aether.cache_store - persists and retrieves a bounded cache value.
    store = aether.cache_store("/tmp/godai-cache.json")
    key = store.key("x", ValueError("bad"))
    store.put(key, "fixed")
    print("11. aether.cache_store:", store.get(key))

    # 12. aether.debounce - suppresses the second identical call.
    print("12. aether.debounce:", debounced_call(1), debounced_call(1))

    # 13. aether.status - reports provider and current connectivity state.
    print("13. aether.status:", aether.status())

    # 14. aether.rust_core - uses the Python reference implementation offline.
    print("14. aether.rust_core:", aether.rust_core("sum", [1, 2]))

    # 15. aether.config - exposes effective resilience settings.
    print("15. aether.config:", aether.config().as_dict())


if __name__ == "__main__":
    main()
