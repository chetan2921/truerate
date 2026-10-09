import mongomock
import pytest

from truerate.db import ensure_indexes


@pytest.fixture
def db():
    database = mongomock.MongoClient().truerate
    ensure_indexes(database)
    return database
