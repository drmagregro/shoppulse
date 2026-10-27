from shoppulse.etl.load_raw import get_connection

# Chaque contrôle : (nom, requête sur raw, requête sur clean, traitement appliqué)
CONTROLES = [
    (
        "Lignes dans geolocation",
        "SELECT COUNT(*) FROM raw.geolocation",
        "SELECT COUNT(*) FROM clean.geolocation",
        "Une seule ligne par code postal (position moyenne)",
    ),
    (
        "Codes postaux en double dans geolocation",
        "SELECT COUNT(*) - COUNT(DISTINCT geolocation_zip_code_prefix) FROM raw.geolocation",
        "SELECT COUNT(*) - COUNT(DISTINCT geolocation_zip_code_prefix) FROM clean.geolocation",
        "Regroupement par code postal (GROUP BY)",
    ),
    (
        "Avis en double (review_id, order_id)",
        "SELECT COUNT(*) - COUNT(DISTINCT (review_id, order_id)) FROM raw.order_reviews",
        "SELECT COUNT(*) - COUNT(DISTINCT (review_id, order_id)) FROM clean.order_reviews",
        "Clé primaire (review_id, order_id) + DISTINCT ON",
    ),
    (
        "Colonnes de dates stockées en texte (table orders)",
        "SELECT COUNT(*) FROM information_schema.columns "
        "WHERE table_schema = 'raw' AND table_name = 'orders' AND data_type = 'text' "
        "AND column_name LIKE 'order_%' AND column_name NOT IN ('order_id', 'order_status')",
        "SELECT COUNT(*) FROM information_schema.columns "
        "WHERE table_schema = 'clean' AND table_name = 'orders' AND data_type = 'text' "
        "AND column_name LIKE 'order_%' AND column_name NOT IN ('order_id', 'order_status')",
        "Conversion en TIMESTAMP",
    ),
    (
        "Commandes livrées sans date de livraison",
        "SELECT COUNT(*) FROM raw.orders "
        "WHERE order_status = 'delivered' AND order_delivered_customer_date IS NULL",
        "SELECT COUNT(*) FROM clean.orders "
        "WHERE order_status = 'delivered' AND order_delivered_customer_date IS NULL",
        "Conservées, mais exclues du modèle de retard",
    ),
    (
        "Livraisons datées avant l'achat",
        "SELECT COUNT(*) FROM raw.orders "
        "WHERE order_delivered_customer_date::TIMESTAMP < order_purchase_timestamp::TIMESTAMP",
        "SELECT COUNT(*) FROM clean.orders "
        "WHERE order_delivered_customer_date < order_purchase_timestamp",
        "Signalées (aucune valeur incohérente si 0)",
    ),
    (
        "Commandes sans aucun article",
        "SELECT COUNT(*) FROM raw.orders o "
        "WHERE NOT EXISTS (SELECT 1 FROM raw.order_items i WHERE i.order_id = o.order_id)",
        "SELECT COUNT(*) FROM clean.orders o "
        "WHERE NOT EXISTS (SELECT 1 FROM clean.order_items i WHERE i.order_id = o.order_id)",
        "Conservées (commandes annulées ou indisponibles), exclues des analyses de panier",
    ),
    (
        "Paiements de montant nul ou négatif",
        "SELECT COUNT(*) FROM raw.order_payments WHERE payment_value::NUMERIC <= 0",
        "SELECT COUNT(*) FROM clean.order_payments WHERE payment_value <= 0",
        "Signalés (bons d'achat probables)",
    ),
    (
        "Produits sans catégorie",
        "SELECT COUNT(*) FROM raw.products WHERE product_category_name IS NULL",
        "SELECT COUNT(*) FROM clean.products WHERE product_category_name IS NULL",
        "Conservés, regroupés sous « inconnue » dans les analyses",
    ),
    (
        "Catégories sans traduction anglaise",
        "SELECT COUNT(DISTINCT p.product_category_name) FROM raw.products p "
        "LEFT JOIN raw.product_category_name_translation t "
        "ON p.product_category_name = t.product_category_name "
        "WHERE p.product_category_name IS NOT NULL AND t.product_category_name IS NULL",
        "SELECT COUNT(DISTINCT p.product_category_name) FROM clean.products p "
        "LEFT JOIN clean.product_category_name_translation t "
        "ON p.product_category_name = t.product_category_name "
        "WHERE p.product_category_name IS NOT NULL AND t.product_category_name IS NULL",
        "Pas de clé étrangère ; nom portugais conservé",
    ),
    (
        "Produits sans poids",
        "SELECT COUNT(*) FROM raw.products WHERE product_weight_g IS NULL",
        "SELECT COUNT(*) FROM clean.products WHERE product_weight_g IS NULL",
        "Exclus du modèle de retard (le poids est une variable)",
    ),
    (
        "Codes postaux clients absents de geolocation",
        "SELECT COUNT(DISTINCT c.customer_zip_code_prefix) FROM raw.customers c "
        "WHERE NOT EXISTS (SELECT 1 FROM raw.geolocation g "
        "WHERE g.geolocation_zip_code_prefix = c.customer_zip_code_prefix)",
        "SELECT COUNT(DISTINCT c.customer_zip_code_prefix) FROM clean.customers c "
        "WHERE NOT EXISTS (SELECT 1 FROM clean.geolocation g "
        "WHERE g.geolocation_zip_code_prefix = c.customer_zip_code_prefix)",
        "Pas de clé étrangère ; distance inconnue pour ces clients",
    ),
]


# Une ligne du tableau Markdown
def ligne_markdown(nom, avant, apres, traitement):
    avant = f"{avant:,}".replace(",", " ")
    apres = f"{apres:,}".replace(",", " ")
    return f"| {nom} | {avant} | {apres} | {traitement} |"


# Lance tous les contrôles et écrit docs/rapport_qualite.md
def generer_rapport(chemin="docs/rapport_qualite.md"):
    conn = get_connection()
    cur = conn.cursor()

    lignes = [
        "# Rapport qualité des données",
        "",
        "Fichier généré automatiquement par le pipeline (`pipelines/etl_flow.py`).",
        "Avant = schéma `raw` (CSV bruts) · Après = schéma `clean` (tables nettoyées).",
        "",
        "| Contrôle | Avant (raw) | Après (clean) | Traitement |",
        "|---|---|---|---|",
    ]

    for nom, sql_avant, sql_apres, traitement in CONTROLES:
        cur.execute(sql_avant)
        avant = cur.fetchone()[0]
        cur.execute(sql_apres)
        apres = cur.fetchone()[0]
        lignes.append(ligne_markdown(nom, avant, apres, traitement))

    conn.close()

    with open(chemin, "w", encoding="utf-8") as f:
        f.write("\n".join(lignes) + "\n")
    print(f"Rapport qualité écrit dans {chemin}")


if __name__ == "__main__":
    generer_rapport()
