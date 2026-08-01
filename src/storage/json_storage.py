"""JSON-file-backed persistence for expense records.

This is the only module in the project that knows expenses live in a
JSON file on disk. If this project ever moved to a real database, only
this file -- and the dependency wiring in ``api/routes.py`` -- would
need to change; ``services`` and ``models`` are storage-agnostic.

Design notes:

- ``add`` and ``delete`` each perform their full read-modify-write cycle
  under a single lock, so a create and a delete happening back-to-back
  can't interleave and corrupt the file or produce a duplicate id.
- IDs are generated as ``max(existing ids) + 1``. This is safe against
  reuse after deletion (a naive "use the record count" scheme would
  reissue a deleted id), though it is not safe across multiple
  *processes* writing to the same file concurrently -- a real deployment
  would need a database with proper unique constraints for that. This
  tradeoff is acceptable for a single-process learning project and is
  called out in the README's Future Improvements section.
"""

import json
from pathlib import Path
from threading import Lock
from typing import Any

from src.utils.exceptions import StorageError

JsonRecord = dict[str, Any]


class JsonStorage:
    """Thread-safe CRUD access to a list-of-objects JSON file."""

    def __init__(self, file_path: Path | str) -> None:
        self._file_path = Path(file_path)
        self._lock = Lock()
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Create the storage file with an empty array if it's missing."""
        if not self._file_path.exists():
            self._file_path.parent.mkdir(parents=True, exist_ok=True)
            self._file_path.write_text("[]", encoding="utf-8")

    def _read(self) -> list[JsonRecord]:
        """Read and parse the storage file, treating an empty file as an empty list.

        Callers must hold ``self._lock`` before calling this.
        """
        raw = self._file_path.read_text(encoding="utf-8").strip()
        if not raw:
            return []
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise StorageError(f"Storage file is not valid JSON: {self._file_path}") from exc
        if not isinstance(data, list):
            raise StorageError(f"Storage file must contain a JSON array: {self._file_path}")
        return data

    def _write(self, records: list[JsonRecord]) -> None:
        """Serialize records to the storage file. Callers must hold ``self._lock``."""
        self._file_path.write_text(
            json.dumps(records, indent=2, default=str),
            encoding="utf-8",
        )

    def list_all(self) -> list[JsonRecord]:
        """Return every stored record."""
        with self._lock:
            return self._read()

    def add(self, data: JsonRecord) -> JsonRecord:
        """Assign a new id to ``data``, persist it, and return the full record."""
        with self._lock:
            records = self._read()
            new_record = {"id": self._next_id(records), **data}
            records.append(new_record)
            self._write(records)
            return new_record

    def delete(self, record_id: int) -> bool:
        """Remove the record with ``record_id``. Returns True if something was deleted."""
        with self._lock:
            records = self._read()
            remaining = [r for r in records if r["id"] != record_id]
            if len(remaining) == len(records):
                return False
            self._write(remaining)
            return True

    @staticmethod
    def _next_id(records: list[JsonRecord]) -> int:
        """Generate the next id as one greater than the current maximum."""
        if not records:
            return 1
        return max(record["id"] for record in records) + 1
