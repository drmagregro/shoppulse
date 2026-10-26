from shoppulse.etl.load_raw import TABLES


# On doit charger les 9 fichiers Olist
def test_il_y_a_9_tables():
    assert len(TABLES) == 9


# Chaque table chargée doit être créée dans le script SQL
def test_chaque_table_existe_dans_le_sql():
    with open("sql/01_raw_schema.sql") as f:
        sql = f.read()
    for table in TABLES:
        assert f"raw.{table}" in sql