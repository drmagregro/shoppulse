from shoppulse.config import Settings


def test_database_url_built_from_settings() -> None:
    s = Settings(
        postgres_user="u", postgres_password="p", postgres_host="h",
        postgres_port=1234, postgres_db="d",
    )
    assert s.database_url == "postgresql+psycopg2://u:p@h:1234/d"
