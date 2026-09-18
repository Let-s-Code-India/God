"""One coherent offline workflow that visits every public godai member."""

import asyncio
from pathlib import Path

from pydantic import BaseModel

from godai import aura, nexus, aether, apex


class Record(BaseModel):
    name: str


class FakeApp:
    """Framework-shaped object for the middleware portion of the workflow."""

    def errorhandler(self, _error):
        return lambda function: function

    def middleware(self, _kind):
        return lambda function: function

    class logger:
        @staticmethod
        def error(*args):
            print(*args)


def run() -> None:
    # 1. aura.heal - protects the workflow's first arithmetic operation.
    @aura.heal(retries=1)
    def add(left: int, right: int) -> int:
        return left + right

    print("1. aura.heal:", add(2, 3))

    # 2. aura.patch - leaves a successful workflow step unchanged.
    @aura.patch()
    def patch_step() -> str:
        return "patched"

    print("2. aura.patch:", patch_step())

    # 3. aura.retry - handles a stable local operation.
    @aura.retry(retries=1)
    def retry_step() -> str:
        return "retried"

    print("3. aura.retry:", retry_step())

    # 4. aura.validate - validates the workflow record result.
    @aura.validate(output_schema=dict)
    def validated_step() -> dict:
        return {"ok": True}

    print("4. aura.validate:", validated_step())

    # 5. aura.trace - records one workflow value.
    @aura.trace
    def traced_step() -> str:
        return "traced"

    print("5. aura.trace:", traced_step())

    # 6. aura.cache - normalizes and caches a repeated text value.
    @aura.cache(semantic=True)
    def cached_step(text: str) -> str:
        return text.strip()

    print("6. aura.cache:", cached_step(" workflow "))

    # 7. aura.async_heal - runs an async workflow step offline.
    @aura.async_heal()
    async def async_step() -> str:
        return "async"

    print("7. aura.async_heal:", asyncio.run(async_step()))

    # 8. aura.sandbox - computes with its allowed builtins.
    @aura.sandbox
    def sandbox_step() -> int:
        return sum(range(3))

    print("8. aura.sandbox:", sandbox_step())

    # 9. aura.explain - annotates an expected local failure.
    @aura.explain
    def explain_step() -> None:
        raise ValueError("workflow demo")

    try:
        explain_step()
    except ValueError as error:
        print("9. aura.explain:", error.__notes__[0])

    # 10. aura.benchmark - measures the next local transformation.
    @aura.benchmark
    def benchmark_step() -> str:
        return "benchmarked"

    print("10. aura.benchmark:", benchmark_step())

    # 11. aura.guard - confirms this offline step has no prerequisites.
    @aura.guard(env=())
    def guard_step() -> str:
        return "guarded"

    print("11. aura.guard:", guard_step())

    # 12. aura.dry_run - marks a side-effect-shaped operation for preview.
    @aura.dry_run()
    def dry_step() -> str:
        return "dry-run"

    print("12. aura.dry_run:", dry_step())

    # 13. aura.audit - records this workflow event locally.
    @aura.audit(path="/tmp/godai-combined.jsonl")
    def audit_step() -> str:
        return "audited"

    print("13. aura.audit:", audit_step())

    # 14. aura.fallback - supplies a value after a deliberate local failure.
    @aura.fallback(default="fallback")
    def fallback_step() -> str:
        raise RuntimeError("offline")

    print("14. aura.fallback:", fallback_step())

    # 15. aura.rate_limit - consumes one token from a local bucket.
    @aura.rate_limit(rate=100, capacity=2)
    def limited_step() -> str:
        return "limited"

    print("15. aura.rate_limit:", limited_step())

    # 16. nexus.explain - diagnoses a workflow exception.
    print("16. nexus.explain:", nexus.explain(KeyError("name")))

    # 17. nexus.parse - parses the record that feeds the next stage.
    print("17. nexus.parse:", nexus.parse("name: demo", Record))

    # 18. nexus.agent - inspects this project without editing it.
    print("18. nexus.agent:", nexus.agent("inspect", "."))

    # 19. nexus.summarize - summarizes the workflow's tiny code sample.
    print("19. nexus.summarize:", nexus.summarize("def ready(): return True"))

    # 20. nexus.review - reviews a deliberately risky diff string.
    print("20. nexus.review:", nexus.review("+ eval(value)"))

    # 21. nexus.test_gen - generates a test for the first workflow step.
    print("21. nexus.test_gen:\n", nexus.test_gen(add))

    # 22. nexus.docstring - describes the arithmetic callable.
    print("22. nexus.docstring:", nexus.docstring(add))

    # 23. nexus.translate - requests an offline translation marker.
    print("23. nexus.translate:", nexus.translate("x = 1", "javascript"))

    # 24. nexus.refactor - requests an offline refactor suggestion.
    print("24. nexus.refactor:", nexus.refactor("x=1", "clarity"))

    # 25. nexus.complexity - calculates complexity from syntax.
    print("25. nexus.complexity:", nexus.complexity("def f(x):\n if x: return 1"))

    # 26. nexus.security_scan - checks the workflow's generated text.
    print("26. nexus.security_scan:", nexus.security_scan("secret = 'demo'"))

    # 27. nexus.dependency_check - inspects this example's imports.
    print("27. nexus.dependency_check:", nexus.dependency_check(__file__))

    # 28. nexus.commit_message - creates a conventional subject.
    print("28. nexus.commit_message:", nexus.commit_message("fix workflow"))

    # 29. nexus.changelog - formats the workflow change list.
    print("29. nexus.changelog:", nexus.changelog(["fix workflow"]))

    # 30. nexus.ask - answers within the supplied workflow context.
    print("30. nexus.ask:", nexus.ask("what is this?", "x = 1"))

    # 31. aether.timeout - bounds a fast local operation.
    @aether.timeout(1)
    def bounded_step() -> str:
        return "bounded"

    print("31. aether.timeout:", bounded_step())

    # 32. aether.circuit_breaker - closes cleanly after one successful call.
    breaker = aether.circuit_breaker("combined")
    print("32. aether.circuit_breaker:", breaker.call(lambda: "closed"))

    # 33. aether.offline_queue - persists a workflow payload.
    queue = aether.offline_queue("/tmp/godai-combined.sqlite3")
    queue.put({"step": "queued"})
    print("33. aether.offline_queue:", queue.get_all())

    # 34. aether.heuristics - diagnoses the known missing-key case.
    print("34. aether.heuristics:", aether.heuristics(KeyError("x")))

    # 35. aether.fallback_provider - selects the local provider.
    print("35. aether.fallback_provider:", aether.fallback_provider([lambda: "local"]))

    # 36. aether.degraded_mode - checks network state for the workflow.
    print("36. aether.degraded_mode:", aether.degraded_mode())

    # 37. aether.lazy_load - loads json only at this point.
    print("37. aether.lazy_load:", aether.lazy_load("json").__name__)

    # 38. aether.zero_overhead - measures a short local loop.
    print("38. aether.zero_overhead:", aether.zero_overhead(10))

    # 39. aether.network_probe - uses a local closed port, avoiding external work.
    print("39. aether.network_probe:", aether.network_probe("127.0.0.1", 9))

    # 40. aether.missing_dependency_helper - verifies json is importable.
    print("40. aether.missing_dependency_helper:", aether.missing_dependency_helper("json"))

    # 41. aether.cache_store - stores a workflow result on disk.
    store = aether.cache_store("/tmp/godai-combined-cache.json")
    store.put("workflow", "cached")
    print("41. aether.cache_store:", store.get("workflow"))

    # 42. aether.debounce - suppresses a duplicate notification.
    @aether.debounce(60)
    def notify_once() -> str:
        return "notified"

    print("42. aether.debounce:", notify_once(), notify_once())

    # 43. aether.status - reports the current resilience state.
    print("43. aether.status:", aether.status())

    # 44. aether.rust_core - uses its offline reference operation.
    print("44. aether.rust_core:", aether.rust_core("sum", [1, 2]))

    # 45. aether.config - captures the effective configuration.
    print("45. aether.config:", aether.config().as_dict())

    # 46. apex.pytest_plugin - creates the test-report integration.
    print("46. apex.pytest_plugin:", apex.pytest_plugin())

    # 47. apex.pre_commit_hook - reviews an empty staged set.
    print("47. apex.pre_commit_hook:", apex.pre_commit_hook([]))

    # 48. apex.github_action - stays offline without GitHub credentials.
    print("48. apex.github_action:", apex.github_action("diff"))

    # 49. apex.django_middleware - constructs optional Django middleware.
    print("49. apex.django_middleware:", apex.django_middleware(lambda request: request))

    # 50. apex.flask_middleware - registers the fake Flask handler.
    app = FakeApp()
    print("50. apex.flask_middleware:", apex.flask_middleware(app))

    # 51. apex.fastapi_middleware - registers the fake ASGI observer.
    print("51. apex.fastapi_middleware:", apex.fastapi_middleware(app))

    # 52. apex.cli - runs the explain command without a subprocess.
    print("52. apex.cli:", apex.cli(["explain", "bad"]))

    # 53. apex.vscode_extension - exposes its local JSON-RPC server contract.
    print("53. apex.vscode_extension:", apex.vscode_extension.__doc__)

    # 54. apex.redact - removes credentials from the workflow payload.
    print("54. apex.redact:", apex.redact("api_key=secret"))

    # 55. apex.on_prem - describes a local compatible provider.
    print("55. apex.on_prem:", apex.on_prem("http://localhost"))

    # 56. apex.multi_tenant - records one team usage unit.
    tenants = apex.multi_tenant("/tmp/godai-combined-tenants.json")
    tenants.add("team", "offline", 2)
    print("56. apex.multi_tenant:", tenants.use("team"))

    # 57. apex.shared_cache - shares the final workflow value locally.
    shared = apex.shared_cache()
    print("57. apex.shared_cache:", shared["put"]("workflow", "shared"))

    # 58. apex.metrics - emits a Prometheus-compatible observation.
    metrics = apex.metrics()
    metrics.observe("heal", 0.01)
    print("58. apex.metrics:", metrics.prometheus())

    # 59. apex.dashboard - renders the local audit history.
    print("59. apex.dashboard:", apex.dashboard("/tmp/godai-combined.jsonl")[:80])

    # 60. apex.docker_ready - validates an empty container requirement set.
    print("60. apex.docker_ready:", apex.docker_ready(()))


if __name__ == "__main__":
    run()
