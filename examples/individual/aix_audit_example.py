"""Standalone aix.audit example."""
from pathlib import Path
from godaix import aix


def main() -> None:
    """Write a structured local exception event."""
    path = Path("/tmp/godaix-aix-audit-example.log")
    print("audit path:", path)
    with aix.audit(path=str(path)):
        print("offline audit event")
    status = {"library": "aix", "member": "audit", "offline": True}
    print("status:", status)
    print("audit event completed")
    print("provider mode: offline")
    print("source remains unchanged")
    print("review complete")
    print("audit example completed")


if __name__ == "__main__":
    main()
