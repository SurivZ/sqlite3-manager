import os
from sqlite3 import OperationalError
import pytest
from sqlite3manager import Connect

TEST_DB_PATH = "test_database.sqlite3"


@pytest.fixture
def db():
    conn = Connect(TEST_DB_PATH, raise_exceptions=True)
    conn.connect()

    yield conn

    conn.close()
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


def test_connection(db):
    assert db.get_status() is True


def test_create_table(db):
    columns = {
        "id": "INTEGER PRIMARY KEY",
        "name": "TEXT",
        "age": "INTEGER"
    }
    result = db.create_table("users", columns)
    assert result is True
    assert "users" in db.list_table_names()
    

def test_create_existing_table(db):
    columns = {
        "id": "INTEGER PRIMARY KEY",
        "name": "TEXT"
    }
    db.create_table("users", columns)

    with pytest.raises(OperationalError) as excinfo:
        db.create_table("users", columns)
    assert "table users already exists" in str(excinfo.value)


def test_insert_and_read(db):
    columns = {
        "id": "INTEGER PRIMARY KEY",
        "name": "TEXT",
        "age": "INTEGER"
    }
    db.create_table("users", columns)

    data = {"id": 1, "name": "John", "age": 30}
    insert_result = db.insert("users", data)
    assert insert_result is True

    rows = db.read_table("users")
    assert len(rows) == 1
    assert rows[0] == (1, "John", 30)


def test_insert_invalid_data(db):
    columns = {
        "id": "INTEGER PRIMARY KEY",
        "name": "TEXT NOT NULL",
        "lastname": "TEXT NOT NULL"
    }
    db.create_table("users", columns, True)

    with pytest.raises(Exception) as excinfo:
        db.insert("users", {"name": "Invalid"})
    assert "insertion failed" in str(excinfo.value)


def test_bulk_insert(db):
    columns = {
        "id": "INTEGER PRIMARY KEY",
        "name": "TEXT",
        "age": "INTEGER"
    }
    db.create_table("users", columns)

    data_list = [
        {"id": 1, "name": "John", "age": 30},
        {"id": 2, "name": "Jane", "age": 25},
        {"id": 3, "name": "Alice", "age": 28},
    ]
    result = db.bulk_insert("users", data_list)
    assert result is True

    rows = db.read_table("users")
    assert len(rows) == 3
    assert rows == [
        (1, "John", 30),
        (2, "Jane", 25),
        (3, "Alice", 28)
    ]


def test_update(db):
    columns = {
        "id": "INTEGER PRIMARY KEY",
        "name": "TEXT",
        "age": "INTEGER"
    }
    db.create_table("users", columns)
    db.insert("users", {"id": 1, "name": "John", "age": 30})

    update_result = db.update("users", {"age": 31}, {"id": 1})
    assert update_result is True

    rows = db.read_table("users")
    assert rows[0] == (1, "John", 31)


def test_delete(db):
    columns = {
        "id": "INTEGER PRIMARY KEY",
        "name": "TEXT",
        "age": "INTEGER"
    }
    db.create_table("users", columns)
    db.insert("users", {"id": 1, "name": "John", "age": 30})

    delete_result = db.delete("users", {"id": 1})
    assert delete_result is True

    rows = db.read_table("users")
    assert len(rows) == 0


def test_add_column(db):
    columns = {
        "id": "INTEGER PRIMARY KEY",
        "name": "TEXT"
    }
    db.create_table("users", columns)
    
    add_result = db.add_column("users", "age", "INTEGER")
    assert add_result is True

    column_names = db.get_column_names("users")
    assert "age" in column_names


def test_drop_column(db):
    columns = {
        "id": "INTEGER PRIMARY KEY",
        "name": "TEXT",
        "age": "INTEGER"
    }
    db.create_table("users", columns)
    db.insert("users", {"id": 1, "name": "John", "age": 30})

    result = db.drop_column("users", "age")
    assert result is True

    remaining_columns = db.get_column_names("users")
    assert "age" not in remaining_columns

    rows = db.read_table("users")
    assert rows == [(1, "John")]


def test_drop_table(db):
    columns = {
        "id": "INTEGER PRIMARY KEY",
        "name": "TEXT",
        "age": "INTEGER"
    }
    db.create_table("users", columns)
    assert "users" in db.list_table_names()

    drop_result = db.drop_table("users")
    assert drop_result is True
    assert "users" not in db.list_table_names()


def test_custom_query(db):
    columns = {
        "id": "INTEGER PRIMARY KEY",
        "name": "TEXT",
        "age": "INTEGER"
    }
    db.create_table("users", columns)
    db.insert("users", {"id": 1, "name": "John", "age": 30})

    result = db.custom_query("SELECT name, age FROM users WHERE id = 1")
    assert result == [("John", 30)]
