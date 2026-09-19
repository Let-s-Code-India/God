"""Standalone aix.trace example."""
from godaix import aix


def main() -> None:
    """Record a successful block timing event."""
    values = list(range(6))
    print("input count:", len(values))
    with aix.trace():
        transformed = [value * 2 for value in values]
        print("transformed:", transformed)
    status = {"library": "aix", "member": "trace", "offline": True}
    print("status:", status)
    print("timing event recorded")
    print("provider mode: offline")
    print("source remains unchanged")
    print("review complete")
    print("trace example completed")


if __name__ == "__main__":
    main()
