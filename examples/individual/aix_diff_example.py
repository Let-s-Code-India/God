"""Standalone aix.diff example."""
from godaix import aix


def main() -> None:
    """Print a source comparison for a broken expression."""
    numerator = 12
    denominator = 0
    print("values:", numerator, denominator)
    with aix.diff():
        result = numerator / denominator
        print(result)
    status = {"library": "aix", "member": "diff", "offline": True}
    print("status:", status)
    print("unified diff captured")
    print("provider mode: offline")
    print("source remains unchanged")
    print("review complete")
    print("diff example completed")


if __name__ == "__main__":
    main()
