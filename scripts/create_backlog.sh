#!/usr/bin/env bash
# Crée les labels et les issues du backlog sur le dépôt GitHub courant.
# Prérequis : CLI gh installée et connectée (brew install gh && gh auth login).
# À lancer UNE seule fois depuis la racine du dépôt : bash scripts/create_backlog.sh
set -euo pipefail

# Labels : un par lot + un pour les jalons
for label in "lot-1:0E8A16" "lot-2:1D76DB" "lot-3:5319E7" "lot-4:D93F0B" "lot-5:FBCA04" "jalon:B60205" "docs:C5DEF5"; do
  name="${label%%:*}"
  color="${label##*:}"
  gh label create "$name" --color "$color" --force
done

issue() {
  # $1 = label, $2 = titre, $3 = échéance
  gh issue create --label "$1" --title "$2" --body "Échéance : $3"
}

issue lot-1 "Note de cadrage (2 pages)" "24 oct."
issue lot-1 "Arbitrage technique argumenté" "24 oct."
issue lot-1 "Schéma d'architecture" "24 oct."
issue lot-1 "Squelette du dépôt, CI GitHub Actions au vert" "24 oct."
issue lot-2 "MLD et schéma SQL des 9 tables" "25 oct."
issue lot-2 "Chargement des 9 CSV dans PostgreSQL" "25 oct."
issue lot-2 "Pipeline ETL Prefect idempotent" "25 oct."
issue lot-2 "Contrôles qualité et rapport avant/après" "26 oct."
issue lot-2 "8 requêtes SQL métier documentées" "26 oct."
issue lot-3 "Notebook EDA (distributions, saisonnalité, géographie)" "27 oct."
issue lot-3 "2 tests statistiques justifiés" "27 oct."
issue lot-3 "Segmentation RFM + clustering, 3 personas, 3 campagnes" "27 oct."
issue jalon "Point d'étape 1" "27 oct."
issue lot-3 "Dashboard Streamlit 5 KPI" "28 oct."
issue lot-4 "Feature engineering (distance, poids, historique vendeur)" "28 oct."
issue lot-4 "Modèle de retard : baseline + 2 algos, validation croisée" "28 oct."
issue lot-4 "Modèle de sentiment : TF-IDF + LR vs réseau de neurones" "29 oct."
issue lot-4 "Audit d'équité par région" "29 oct."
issue jalon "Point d'étape 2" "29 oct."
issue lot-5 "Endpoints FastAPI (un par modèle)" "30 oct."
issue lot-5 "Tests pytest, couverture >= 50 %" "30 oct."
issue lot-5 "Dockerfile et docker-compose de l'API" "30 oct."
issue docs "Note éthique (1 page)" "31 oct."
issue docs "README final testé sur un clone propre" "31 oct."
issue docs "Rétrospective : écarts avec la feuille de route" "31 oct."
issue docs "Support de présentation + vidéo 10 min" "1er nov."

echo "Backlog créé. Ajoute les issues au GitHub Project depuis l'onglet Projects."
