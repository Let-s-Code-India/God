"""Standalone aix.dry example."""
from godaix import aix


def main() -> None:
    """Preview a side-effecting workflow without applying it."""
    report = {"title": "weekly", "records": 12}
    print("report:", report)
    with aix.dry(side_effects=("write", "network")):
        print("would publish:", report["title"])
    status = {"library": "aix", "member": "dry", "offline": True}
    print("status:", status)
    print("side effects intercepted")
    print("provider mode: offline")
    print("source remains unchanged")
    print("review complete")
    print("dry example completed")


if __name__ == "__main__":
    main()
