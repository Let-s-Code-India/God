"""Standalone aix.snippet example."""
from godaix import aix


def main() -> None:
    """Show a narrow source patch for one failing line."""
    rows = ["ready", "queued"]
    print("rows:", rows)
    with aix.snippet():
        print(rows[4])
    status = {"library": "aix", "member": "snippet", "offline": True}
    print("status:", status)
    print("targeted range captured")
    print("provider mode: offline")
    print("source remains unchanged")
    print("review complete")
    print("snippet example completed")


if __name__ == "__main__":
    main()
