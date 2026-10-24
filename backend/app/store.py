"""Canonical data in SQLite; indexes can always be rebuilt from these records."""
import json
import sqlite3
import threading
from contextlib import closing
from datetime import datetime, timezone


def now():
    return datetime.now(timezone.utc).isoformat()


class Store:
    def __init__(self, directory):
        directory.mkdir(parents=True, exist_ok=True)
        self.path = directory / "hub.sqlite3"
        self.lock = threading.RLock()
        self.db = sqlite3.connect(self.path, check_same_thread=False)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("CREATE TABLE IF NOT EXISTS records (kind TEXT, tenant TEXT, id TEXT, body TEXT, PRIMARY KEY(kind,tenant,id))")
        self.db.commit()

    def put(self, kind, tenant, id, body):
        with self.lock, self.db:
            self.db.execute("INSERT OR REPLACE INTO records VALUES (?,?,?,?)", (kind, tenant, id, json.dumps(body)))

    def get(self, kind, tenant, id):
        with self.lock:
            row = self.db.execute("SELECT body FROM records WHERE kind=? AND tenant=? AND id=?", (kind, tenant, id)).fetchone()
        return json.loads(row[0]) if row else None

    def list(self, kind, tenant):
        with self.lock:
            rows = self.db.execute("SELECT body FROM records WHERE kind=? AND tenant=? ORDER BY rowid DESC", (kind, tenant)).fetchall()
        return [json.loads(r[0]) for r in rows]

    def delete(self, kind, tenant, id):
        with self.lock, self.db:
            self.db.execute("DELETE FROM records WHERE kind=? AND tenant=? AND id=?", (kind, tenant, id))

    def trace(self, tenant, run, node, detail, **kwargs):
        import uuid
        event = {"id": uuid.uuid4().hex, "run_id": run, "node": node, "detail": detail, "timestamp": now(), **kwargs}
        self.put("trace", tenant, event["id"], event)
        return event

    def backup(self, destination):
        with self.lock, closing(sqlite3.connect(destination)) as target:
            self.db.backup(target)
