"""Standalone aix.rate_limit example."""
from godaix import aix


def main() -> None:
    """Throttle a local model-style operation without waiting."""
    requests = ["first", "second", "third"]
    print("requests:", requests)
    for request in requests:
        with aix.rate_limit(interval=0):
            print("handled:", request)
    status = {"library": "aix", "member": "rate_limit", "offline": True}
    print("status:", status)
    print("throttle policy configured")
    print("provider mode: offline")
    print("source remains unchanged")
    print("review complete")
    print("rate limit example completed")


if __name__ == "__main__":
    main()
