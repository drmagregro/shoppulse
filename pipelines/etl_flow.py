from prefect import flow, task

from shoppulse.etl.load_raw import TABLES, get_connection, load_table
from shoppulse.etl.quality import generer_rapport


# Tâche 1 : créer le schéma raw et ses tables
@task(retries=2)
def creer_schema():
    conn = get_connection()
    cur = conn.cursor()
    with open("sql/01_raw_schema.sql") as f:
        cur.execute(f.read())
    conn.commit()
    conn.close()


# Tâche 2 : charger un CSV dans sa table
@task(retries=2)
def charger_table(table, fichier):
    conn = get_connection()
    cur = conn.cursor()
    nb = load_table(cur, table, fichier)
    conn.commit()
    conn.close()
    print(f"raw.{table} : {nb} lignes")


# Tâche 3 : créer les tables nettoyées (schéma clean)
@task(retries=2)
def creer_clean():
    conn = get_connection()
    cur = conn.cursor()
    with open("sql/02_clean_schema.sql") as f:
        cur.execute(f.read())
    conn.commit()
    conn.close()


# Tâche 4 : contrôles qualité avant/après, écrits dans docs/rapport_qualite.md
@task
def rapport_qualite():
    generer_rapport()


# Le pipeline : schéma raw, chargement des 9 tables, schéma clean, rapport qualité
@flow(log_prints=True)
def pipeline_etl():
    creer_schema()
    for table in TABLES:
        charger_table(table, TABLES[table])
    creer_clean()
    rapport_qualite()


if __name__ == "__main__":
    pipeline_etl()