"""Standalone aether.offline_queue example."""
from godaix import aether


def main() -> None:
    """Inspect one public member in an offline-friendly project."""
    dataset = [
        {"id": 1, "status": "ready"},
        {"id": 2, "status": "queued"},
    ]
    print("dataset:", dataset)
    member = getattr(aether, "offline_queue")
    print("member:", member.__name__)
    print("doc:", (member.__doc__ or "").splitlines()[0])
    records = [item for item in dataset if item["status"] != "queued"]
    print("selected:", records)
    summary = {"library": "aether", "member": "offline_queue", "count": len(records)}
    print("summary:", summary)
    return None


if __name__ == "__main__":
    main()
