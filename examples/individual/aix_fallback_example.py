"""Standalone aix.fallback example."""
from godaix import aix


def main() -> None:
    """Use a default policy for a failed block."""
    fallback_value = {"source": "offline", "items": []}
    print("fallback value:", fallback_value)
    with aix.fallback(default=fallback_value) as context:
        print("context:", context.value)
        raise ValueError("demo failure")
    status = {"library": "aix", "member": "fallback", "offline": True}
    print("status:", status)
    print("default policy configured")
    print("provider mode: offline")
    print("source remains unchanged")
    print("review complete")
    print("fallback example completed")


if __name__ == "__main__":
    main()
