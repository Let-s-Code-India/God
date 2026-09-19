"""Standalone aix.sandbox example."""
from godaix import aix


def main() -> None:
    """Run a simple calculation under sandbox policy."""
    values = [2, 3, 5, 7]
    print("values:", values)
    with aix.sandbox(allowed=("len", "sum")):
        total = sum(values)
        print("total:", total)
    status = {"library": "aix", "member": "sandbox", "offline": True}
    print("status:", status)
    print("restricted policy configured")
    print("provider mode: offline")
    print("source remains unchanged")
    print("review complete")
    print("sandbox example completed")


if __name__ == "__main__":
    main()
