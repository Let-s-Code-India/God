"""Standalone aix.benchmark example."""
from godaix import aix


def main() -> None:
    """Measure a small deterministic calculation."""
    values = list(range(100))
    print("benchmark size:", len(values))
    with aix.benchmark():
        total = sum(value * value for value in values)
        print("square total:", total)
    status = {"library": "aix", "member": "benchmark", "offline": True}
    print("status:", status)
    print("timing measurement recorded")
    print("provider mode: offline")
    print("source remains unchanged")
    print("review complete")
    print("benchmark example completed")


if __name__ == "__main__":
    main()
