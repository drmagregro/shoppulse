import psycopg2

from shoppulse.config import settings

# Chaque table du schéma raw et le CSV qui la remplit
TABLES = {
    "sellers": "olist_sellers_dataset.csv",
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "products": "olist_products_dataset.csv",
    "product_category_name_translation": "product_category_name_translation.csv",
}


def load_table(cur, table, filename):
    """Vide la table puis la remplit avec le CSV. Renvoie le nombre de lignes."""
    cur.execute(f"TRUNCATE raw.{table}")
    with open(f"data/raw/{filename}", encoding="utf-8") as f:
        cur.copy_expert(f"COPY raw.{table} FROM STDIN WITH (FORMAT csv, HEADER)", f)
    cur.execute(f"SELECT COUNT(*) FROM raw.{table}")
    return cur.fetchone()[0]


conn = psycopg2.connect(
    host=settings.postgres_host,
    port=settings.postgres_port,
    user=settings.postgres_user,
    password=settings.postgres_password,
    dbname=settings.postgres_db,
)
cur = conn.cursor()

for table, filename in TABLES.items():
    nb = load_table(cur, table, filename)
    print(f"raw.{table} : {nb} lignes")

conn.commit()
conn.close()