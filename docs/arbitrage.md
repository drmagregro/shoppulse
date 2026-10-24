# Arbitrages techniques

Chaque choix est évalué selon les quatre critères demandés : coût, délai, performance, pérennité.
Contexte décisif : **10 jours, une seule personne, exécution locale**.

## 1. Orchestration : Prefect vs Airflow

| Critère | Prefect 2 | Airflow |
|---|---|---|
| Coût | Gratuit, open source, aucune infrastructure à faire tourner | Gratuit mais demande un scheduler, un webserver et une base de métadonnées |
| Délai | Un flow = des fonctions Python avec `@flow` / `@task`, exécutable avec `python flow.py` | Installation et configuration plus lourdes, surtout sous Docker |
| Performance | Largement suffisante pour 9 CSV et environ 100 000 commandes | Également suffisante, pensé pour des charges bien plus grandes |
| Pérennité | Communauté active, offre cloud managée disponible | Standard du marché, très répandu en entreprise |

**Décision : Prefect.**
Airflow est le standard en entreprise, et je le connais. Mais sur 10 jours, son coût de mise en place (scheduler, webserver, base de métadonnées) consomme du temps sans apporter de valeur à ce volume de données. Prefect donne les mêmes garanties utiles ici (retries, logs, suivi des tâches) avec du Python pur, testable avec pytest.
**Condition de révision :** si ShopPulse dispose déjà d'un Airflow en production, les tâches Prefect se transposent facilement en DAG, car la logique métier vit dans le package `shoppulse` et non dans l'orchestrateur.

## 2. Dashboard : Streamlit vs Metabase

| Critère | Streamlit | Metabase |
|---|---|---|
| Coût | Gratuit, open source | Gratuit en version open source |
| Délai | Écrit en Python, réutilise directement le code du projet | Rapide pour des graphiques simples, en cliquant |
| Performance | Requêtes SQL directes + cache intégré | Bonne, requêtes directes sur la base |
| Pérennité | Versionné dans Git comme le reste du code | Configuration stockée dans la base interne de Metabase, plus dure à versionner |

**Décision : Streamlit.**
Le dashboard reste dans le dépôt, versionné et reproductible par un tiers, ce qui sert directement le critère « clonable en moins de 30 minutes ». Il peut aussi afficher les segments et les prédictions des modèles sans outil supplémentaire.
**Limite assumée :** un utilisateur métier ne peut pas créer ses propres graphiques, contrairement à Metabase. Pour une adoption large par les équipes, Metabase serait à reconsidérer.

## 3. Sentiment sur des avis en portugais

| Option | Avantage | Inconvénient |
|---|---|---|
| Traduction vers l'anglais | Accès aux modèles anglais | Coût et délai de traduction de dizaines de milliers d'avis, perte de nuances |
| Modèle multilingue pré-entraîné | Bonnes performances sans entraînement | Lourd à servir dans l'API et dans la CI |
| **Entraînement direct sur le portugais** | Simple, léger, cohérent avec la consigne baseline vs réseau de neurones | Pas de connaissance linguistique préalable |

**Décision : entraînement direct.**
Le label est dérivé de la note (1-2 = négatif, 4-5 = positif, 3 exclu ou traité à part). TF-IDF et un petit réseau de neurones apprennent directement le vocabulaire portugais, sans dépendance lourde dans l'image Docker.
