"""Load explicitly synthetic runbooks into canonical storage; no model calls."""
import json
from pathlib import Path
from backend.app.config import Settings
from backend.app.store import Store, now


def seed(store):
    root = Path(__file__).resolve().parents[1]
    for doc in json.loads((root / "data/runbooks.json").read_text()):
        if not store.get("document", "local", doc["id"]):
            store.put("document", "local", doc["id"], {**doc, "created_at": now(), "synthetic": True})


if __name__ == "__main__":
    seed(Store(Settings.from_env().data_dir))
    print("Synthetic runbooks loaded. No cloud calls made.")
