"""Offline, individually labeled examples for every Aura decorator."""

import asyncio

from pydantic import BaseModel

from godai import aura


# 1. aura.heal - diagnoses a failure and retries it.
@aura.heal(retries=1)
def healed_add(left: int, right: int) -> int:
    return left + right


# 2. aura.patch - keeps a successful function unchanged.
@aura.patch()
def patchable_value() -> int:
    return 7


# 3. aura.retry - retries transient failures with backoff.
@aura.retry(retries=1)
def stable_value() -> str:
    return "stable"


class Result(BaseModel):
    value: int


# 4. aura.validate - validates a returned Pydantic model.
@aura.validate(output_schema=Result)
def validated_result() -> dict:
    return {"value": 3}


# 5. aura.trace - records arguments and the return value.
@aura.trace
def traced_value() -> str:
    return "traced"


# 6. aura.cache - reuses a result after semantic whitespace normalization.
@aura.cache(semantic=True)
def normalized_text(text: str) -> str:
    return text.strip().lower()


# 7. aura.async_heal - wraps an async function without provider access.
@aura.async_heal()
async def async_value() -> int:
    return 4


# 8. aura.sandbox - permits the restricted builtins used by this function.
@aura.sandbox
def sandbox_sum() -> int:
    return sum(range(4))


# 9. aura.explain - adds an offline explanation to a raised error.
@aura.explain
def explained_failure() -> None:
    raise ValueError("demo")


# 10. aura.benchmark - logs timing around a simple call.
@aura.benchmark
def benchmarked_value() -> str:
    return "benchmarked"


# 11. aura.guard - allows this call because it has no prerequisites.
@aura.guard(env=())
def guarded_value() -> str:
    return "guarded"


# 12. aura.dry_run - records configured side effects while calling the function.
@aura.dry_run()
def dry_run_value() -> str:
    return "preview"


# 13. aura.audit - writes a call and success event to a JSON-lines file.
@aura.audit(path="/tmp/godai-aura-example.jsonl")
def audited_value() -> str:
    return "audited"


# 14. aura.fallback - returns a default after the primary function fails.
@aura.fallback(default="fallback")
def fallback_value() -> str:
    raise RuntimeError("offline demo failure")


# 15. aura.rate_limit - permits the first token-bucket call.
@aura.rate_limit(rate=100, capacity=2)
def limited_value() -> str:
    return "rate-limited"


def main() -> None:
    print("1. aura.heal:", healed_add(2, 3))
    print("2. aura.patch:", patchable_value())
    print("3. aura.retry:", stable_value())
    print("4. aura.validate:", validated_result())
    print("5. aura.trace:", traced_value())
    print("6. aura.cache:", normalized_text(" Hello "))
    print("7. aura.async_heal:", asyncio.run(async_value()))
    print("8. aura.sandbox:", sandbox_sum())
    try:
        explained_failure()
    except ValueError as error:
        print("9. aura.explain:", error.__notes__[0])
    print("10. aura.benchmark:", benchmarked_value())
    print("11. aura.guard:", guarded_value())
    print("12. aura.dry_run:", dry_run_value())
    print("13. aura.audit:", audited_value())
    print("14. aura.fallback:", fallback_value())
    print("15. aura.rate_limit:", limited_value())


if __name__ == "__main__":
    main()
