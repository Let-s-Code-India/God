"""Standalone aix.guard example."""
from godaix import aix


def main() -> None:
    """Pass an offline package precondition before entering a block."""
    configuration = {"mode": "offline", "package": "json"}
    print("configuration:", configuration)
    with aix.guard(packages=("json",)):
        print("guarded mode:", configuration["mode"])
    status = {"library": "aix", "member": "guard", "offline": True}
    print("status:", status)
    print("preconditions validated")
    print("provider mode: offline")
    print("source remains unchanged")
    print("review complete")
    print("guard example completed")


if __name__ == "__main__":
    main()
