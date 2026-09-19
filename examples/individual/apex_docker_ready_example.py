"""Standalone apex.docker_ready example."""
from godaix import apex


def main() -> None:
    """Inspect one public member in an offline-friendly project."""
    dataset = [
        {"id": 1, "status": "ready"},
        {"id": 2, "status": "queued"},
    ]
    print("dataset:", dataset)
    member = getattr(apex, "docker_ready")
    print("member:", member.__name__)
    print("doc:", (member.__doc__ or "").splitlines()[0])
    records = [item for item in dataset if item["status"] != "queued"]
    print("selected:", records)
    summary = {"library": "apex", "member": "docker_ready", "count": len(records)}
    print("summary:", summary)
    return None


if __name__ == "__main__":
    main()
