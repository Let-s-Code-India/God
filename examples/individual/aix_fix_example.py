"""Standalone aix.fix example."""
from godaix import aix


def main() -> None:
    """Run a deliberately failing block for local repair."""
    values = [4, 8, 12]
    print("input values:", values)
    with aix.fix():
        result = values[0] / 0
        print(result)
    status = {"library": "aix", "member": "fix", "offline": True}
    print("status:", status)
    print("captured block only")
    print("provider mode: offline")
    print("no file was written")
    print("review complete")
    print("fix example completed")


if __name__ == "__main__":
    main()
