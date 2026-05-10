from app.core.config import Settings


def test_postgresql_url_uses_psycopg_driver():
    settings = Settings(database_url="postgresql://user:pass@localhost/dbname")

    assert settings.sqlalchemy_database_url == "postgresql+psycopg://user:pass@localhost/dbname"


def test_explicit_driver_url_is_preserved():
    settings = Settings(database_url="postgresql+psycopg://user:pass@localhost/dbname")

    assert settings.sqlalchemy_database_url == "postgresql+psycopg://user:pass@localhost/dbname"
