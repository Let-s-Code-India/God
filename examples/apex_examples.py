"""Offline, individually labeled examples for every Apex integration."""

from godai import apex


class FakeApp:
    """Small framework-shaped object used by the middleware examples."""

    def errorhandler(self, _error):
        return lambda function: function

    def middleware(self, _kind):
        return lambda function: function

    class logger:
        @staticmethod
        def error(*args):
            print(*args)


def main() -> None:
    app = FakeApp()

    # 1. apex.pytest_plugin - creates a pytest report hook object.
    print("1. apex.pytest_plugin:", apex.pytest_plugin())

    # 2. apex.pre_commit_hook - reviews an explicitly empty staged set.
    print("2. apex.pre_commit_hook:", apex.pre_commit_hook([]))

    # 3. apex.github_action - reports missing credentials without network access.
    print("3. apex.github_action:", apex.github_action("diff"))

    # 4. apex.django_middleware - constructs guarded middleware offline.
    django_class = apex.django_middleware(lambda request: request)
    print("4. apex.django_middleware:", django_class)

    # 5. apex.flask_middleware - registers a handler on the fake app.
    print("5. apex.flask_middleware:", apex.flask_middleware(app))

    # 6. apex.fastapi_middleware - registers middleware on the fake app.
    print("6. apex.fastapi_middleware:", apex.fastapi_middleware(app))

    # 7. apex.cli - executes the offline explain command.
    print("7. apex.cli:", apex.cli(["explain", "KeyError('x')"]))

    # 8. apex.vscode_extension - exposes a documented server callable.
    print("8. apex.vscode_extension:", apex.vscode_extension.__doc__)

    # 9. apex.redact - removes a secret before transport.
    print("9. apex.redact:", apex.redact("api_key=secret@example.com"))

    # 10. apex.on_prem - describes an OpenAI-compatible local endpoint.
    print("10. apex.on_prem:", apex.on_prem("http://localhost:8000"))

    # 11. apex.multi_tenant - adds and consumes one tenant quota unit.
    tenants = apex.multi_tenant("/tmp/godai-tenants.json")
    tenants.add("team", "key", 2)
    print("11. apex.multi_tenant:", tenants.use("team"))

    # 12. apex.shared_cache - writes through the local cache adapter.
    cache = apex.shared_cache()
    print("12. apex.shared_cache:", cache["put"]("x", 1))

    # 13. apex.metrics - records and renders one observation.
    metrics = apex.metrics()
    metrics.observe("heal", 0.01)
    print("13. apex.metrics:", metrics.prometheus())

    # 14. apex.dashboard - renders an empty local audit view.
    print("14. apex.dashboard:", apex.dashboard("/tmp/missing-audit.jsonl")[:30])

    # 15. apex.docker_ready - validates an empty requirement set.
    print("15. apex.docker_ready:", apex.docker_ready(()))


if __name__ == "__main__":
    main()
