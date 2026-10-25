import psycopg2

from shoppulse.config import settings

conn = psycopg2.connect(
    host=settings.postgres_host,
    port=settings.postgres_port,
    user=settings.postgres_user,
    password=settings.postgres_password,
    dbname=settings.postgres_db,
)
cur = conn.cursor()
cur.execute("TRUNCATE raw.sellers")
with open("data/raw/olist_sellers_dataset.csv", encoding="utf-8") as f:
    cur.copy_expert("COPY raw.sellers FROM STDIN WITH (FORMAT csv, HEADER)", f)
conn.commit()

cur.execute("SELECT COUNT(*) FROM raw.sellers")
print(cur.fetchone())
conn.close()