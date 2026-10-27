# Rapport qualité des données

Fichier généré automatiquement par le pipeline (`pipelines/etl_flow.py`).
Avant = schéma `raw` (CSV bruts) · Après = schéma `clean` (tables nettoyées).

| Contrôle | Avant (raw) | Après (clean) | Traitement |
|---|---|---|---|
| Lignes dans geolocation | 1 000 163 | 19 015 | Une seule ligne par code postal (position moyenne) |
| Codes postaux en double dans geolocation | 981 148 | 0 | Regroupement par code postal (GROUP BY) |
| Avis en double (review_id, order_id) | 0 | 0 | Clé primaire (review_id, order_id) + DISTINCT ON |
| Colonnes de dates stockées en texte (table orders) | 5 | 0 | Conversion en TIMESTAMP |
| Commandes livrées sans date de livraison | 8 | 8 | Conservées, mais exclues du modèle de retard |
| Livraisons datées avant l'achat | 0 | 0 | Signalées (aucune valeur incohérente si 0) |
| Commandes sans aucun article | 775 | 775 | Conservées (commandes annulées ou indisponibles), exclues des analyses de panier |
| Paiements de montant nul ou négatif | 9 | 9 | Signalés (bons d'achat probables) |
| Produits sans catégorie | 610 | 610 | Conservés, regroupés sous « inconnue » dans les analyses |
| Catégories sans traduction anglaise | 2 | 2 | Pas de clé étrangère ; nom portugais conservé |
| Produits sans poids | 2 | 2 | Exclus du modèle de retard (le poids est une variable) |
| Codes postaux clients absents de geolocation | 157 | 157 | Pas de clé étrangère ; distance inconnue pour ces clients |
