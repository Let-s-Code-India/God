"""Standalone aix.repl example."""
from godaix import aix


def main() -> None:
    """Demonstrate the interactive repair surface without applying changes."""
    values = [1, 2, 3]
    print("values:", values)
    print("repl is interactive; this sample is opt-in when run manually")
    if False:
        with aix.repl():
            print(values[8])
    status = {"library": "aix", "member": "repl", "offline": True}
    print("status:", status)
    print("interactive mode is opt in")
    print("provider mode: offline")
    print("source remains unchanged")
    print("review complete")
    print("repl example completed")


if __name__ == "__main__":
    main()
