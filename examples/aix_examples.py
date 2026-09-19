"""Coherent offline tour of all fifteen godaix.aix context managers."""
from pathlib import Path

from godaix import aix


def main() -> None:
    """Run block-level controls around a small deployment preparation job."""
    records = [{"name": "alpha", "ready": True}, {"name": "beta", "ready": False}]
    # aix.fix: protect the validation block.
    with aix.fix():
        result = [record for record in records if record["ready"]]
        print("fix result:", result)
    # aix.explain: inspect a normal block without failure.
    with aix.explain():
        print("explain records:", len(records))
    # aix.snippet: keep a narrow source window around a block.
    with aix.snippet():
        print("snippet first:", records[0]["name"])
    # aix.diff: compare a candidate block when it fails.
    with aix.diff():
        print("diff count:", len(records))
    # aix.file_patch: reserve broader repairs for explicit failures.
    with aix.file_patch():
        print("file patch path:", Path(__file__).name)
    # aix.retry: bound a transient operation.
    with aix.retry(attempts=2, backoff=0):
        print("retry complete")
    # aix.fallback: provide a stable local default.
    with aix.fallback(default=[]):
        print("fallback ready")
    # aix.dry: document side effects without making any.
    with aix.dry(side_effects=("write", "network")):
        print("dry deployment")
    # aix.sandbox: mark a restricted calculation.
    with aix.sandbox():
        print("sandbox total:", sum(record["ready"] for record in records))
    # aix.guard: validate an installed standard-library package.
    with aix.guard(packages=("json",)):
        print("guard passed")
    # aix.trace: record the block timing.
    with aix.trace():
        print("trace records:", records)
    # aix.benchmark: measure deterministic work.
    with aix.benchmark():
        print("benchmark total:", sum(range(20)))
    # aix.audit: successful blocks need no audit event.
    audit_path = "/tmp/godaix-aix-example.log"
    with aix.audit(path=audit_path):
        print("audit destination:", audit_path)
    # aix.rate_limit: make repeated provider calls observable.
    with aix.rate_limit(interval=0):
        print("rate limited request")
    # aix.repl: keep interactive editing opt-in for automation.
    if False:
        with aix.repl():
            print("interactive repair")
    print("aix tour completed")


if __name__ == "__main__":
    main()
