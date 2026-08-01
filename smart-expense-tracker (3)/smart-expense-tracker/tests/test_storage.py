"""Tests for JsonStorage: file handling and id generation."""

from pathlib import Path

import pytest

from src.storage.json_storage import JsonStorage
from src.utils.exceptions import StorageError


def test_creates_file_with_empty_array_if_missing(storage_path: Path) -> None:
    assert not storage_path.exists()
    JsonStorage(storage_path)
    assert storage_path.exists()
    assert storage_path.read_text().strip() == "[]"


def test_treats_empty_file_as_empty_list(storage_path: Path) -> None:
    storage_path.write_text("")
    storage = JsonStorage(storage_path)
    assert storage.list_all() == []


def test_raises_storage_error_on_corrupted_json(storage_path: Path) -> None:
    storage_path.write_text("{not valid json")
    storage = JsonStorage(storage_path)
    with pytest.raises(StorageError):
        storage.list_all()


def test_raises_storage_error_if_root_is_not_a_list(storage_path: Path) -> None:
    storage_path.write_text('{"not": "a list"}')
    storage = JsonStorage(storage_path)
    with pytest.raises(StorageError):
        storage.list_all()


def test_add_assigns_incrementing_ids(storage: JsonStorage) -> None:
    first = storage.add({"title": "Coffee", "amount": 4.5})
    second = storage.add({"title": "Tea", "amount": 3.0})
    assert first["id"] == 1
    assert second["id"] == 2


def test_add_does_not_reuse_id_after_deletion(storage: JsonStorage) -> None:
    first = storage.add({"title": "Coffee", "amount": 4.5})
    storage.add({"title": "Tea", "amount": 3.0})
    storage.delete(first["id"])
    third = storage.add({"title": "Cake", "amount": 6.0})
    # id 1 was deleted; the next id should be 3, not a reused 1.
    assert third["id"] == 3


def test_delete_returns_true_when_record_existed(storage: JsonStorage) -> None:
    record = storage.add({"title": "Coffee", "amount": 4.5})
    assert storage.delete(record["id"]) is True
    assert storage.list_all() == []


def test_delete_returns_false_when_record_missing(storage: JsonStorage) -> None:
    assert storage.delete(999) is False


def test_list_all_returns_all_records(storage: JsonStorage) -> None:
    storage.add({"title": "Coffee", "amount": 4.5})
    storage.add({"title": "Tea", "amount": 3.0})
    assert len(storage.list_all()) == 2
