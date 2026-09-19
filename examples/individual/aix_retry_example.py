"""Standalone aix.retry example."""
from godaix import aix


def main() -> None:
    """Exercise the bounded retry context with stable local work."""
    attempts = ["cache", "cache", "ready"]
    print("attempt plan:", attempts)
    with aix.retry(attempts=3, backoff=0):
        result = attempts[-1]
        print("selected:", result)
    status = {"library": "aix", "member": "retry", "offline": True}
    print("status:", status)
    print("transient policy configured")
    print("provider mode: offline")
    print("source remains unchanged")
    print("review complete")
    print("retry example completed")


if __name__ == "__main__":
    main()
