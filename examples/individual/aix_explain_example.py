"""Standalone aix.explain example."""
from godaix import aix


def main() -> None:
    """Show a diagnosis without requesting replacement code."""
    record = {"name": "Ada", "score": 98}
    print("record keys:", sorted(record))
    with aix.explain():
        print(record["missing"])
    status = {"library": "aix", "member": "explain", "offline": True}
    print("status:", status)
    print("diagnosis remains local")
    print("provider mode: offline")
    print("source remains unchanged")
    print("review complete")
    print("diagnosis example completed")


if __name__ == "__main__":
    main()
