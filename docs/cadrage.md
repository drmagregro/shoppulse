# Note de cadrage — ShopPulse Mission Flash

**Consultant :** Matteo Bruno · **Durée :** 10 jours · **Rendu :** 2 novembre, 17h00
**Commanditaire :** Directeur Data de ShopPulse

## 1. Contexte

ShopPulse est une marketplace e-commerce de taille moyenne : environ 3 000 vendeurs et 100 000 clients. Les données utilisées sont celles du dataset public Olist (Brésil, 2016-2018, environ 100 000 commandes réparties dans 9 fichiers CSV), présentées comme celles de ShopPulse.

## 2. Enjeux métier

La direction exprime trois irritants, chacun relié à un enjeu :

| Irritant | Conséquence | Enjeu |
|---|---|---|
| Données éparpillées, pas de vision consolidée | Décisions prises sans chiffres fiables communs | Une source de vérité unique |
| Marketing non segmenté, réachat qui stagne | Budget dilué, clients fidèles traités comme les autres | Cibler et faire revenir les clients |
| Retards découverts via les avis négatifs | Réputation dégradée, réaction trop tardive | Anticiper les retards avant la livraison |

## 3. Objectifs et indicateurs de succès

| Objectif | Livrable | Indicateur de succès |
|---|---|---|
| Base consolidée et fiable | PostgreSQL alimentée par un pipeline rejouable | 9 tables chargées, contrôles qualité passants, rapport avant/après |
| Mieux cibler | Segmentation RFM + clustering, 3 personas | 3 campagnes chiffrées (cible, coût, gain estimé) |
| Anticiper les retards | Modèle de classification + endpoint API | Rappel sur la classe « retard » supérieur à la baseline |
| Comprendre les avis | Modèle de sentiment | F1 du réseau de neurones comparé à TF-IDF + régression logistique |
| Piloter l'activité | Dashboard 5 KPI | Lisible par un non-technicien sans explication |

**Objectifs économiques (hypothèses à confirmer pendant l'EDA) :**
- **Réachat** : la très grande majorité des clients Olist n'achète qu'une seule fois. Faire passer même une petite part de ces clients à une seconde commande représente un chiffre d'affaires supplémentaire qui sera chiffré à partir du panier moyen mesuré.
- **Retards** : une commande en retard reçoit en moyenne une note nettement plus basse. Détecter les commandes à risque permet de prévenir le client ou de prioriser l'expédition avant que l'avis négatif ne soit écrit.

## 4. Utilisateurs

| Utilisateur | Besoin | Forme de la réponse |
|---|---|---|
| Direction | Savoir comment se porte l'activité | Page de dashboard, 5 KPI |
| Marketing | Savoir qui cibler et comment | Personas + campagnes chiffrées |
| Logistique | Savoir quelles commandes vont arriver en retard | Score de risque via l'API |
| Service client | Savoir ce que disent les avis | Sentiment prédit par avis |
| Équipe data | Maintenir et rejouer la chaîne | Pipeline, tests, Docker, CI |

## 5. Périmètre

**Dans le périmètre :** les 9 CSV Olist, PostgreSQL, pipeline ETL orchestré, EDA et tests statistiques, segmentation, dashboard, deux modèles, API FastAPI conteneurisée, CI GitHub Actions, note éthique.

**Hors périmètre :** Spark, ELK, déploiement AWS, dataset REES46. Bonus envisagés seulement si les 5 lots sont livrés, par ordre de priorité : suivi MLflow, puis déploiement cloud.

## 6. Contraintes et risques

| Risque | Impact | Parade |
|---|---|---|
| Délai de 10 jours, projet individuel | Lots incomplets | Livrer le minimum de chaque lot avant d'approfondir |
| Avis en portugais | Modèle de sentiment moins bon | Entraînement direct sur le portugais (stratégie justifiée au lot 4) |
| Classes déséquilibrées (peu de retards) | Accuracy trompeuse | Rappel, F1, PR-AUC, pondération des classes |
| Données personnelles (codes postaux, villes) | Non-conformité RGPD | Aucune donnée complète dans le dépôt, analyse à la maille région |
| Dépôt non exécutable | Lot 5 non évalué | README testé sur un clone propre avant le rendu |

## 7. Évolutions probables

- Scoring du retard en temps réel au moment de la commande, branché sur le système logistique.
- Rafraîchissement automatique quotidien du pipeline et du dashboard.
- Réentraînement périodique des modèles avec suivi des performances (MLflow).
- Passage à l'échelle avec Spark si les volumes ou le clickstream (REES46) sont intégrés.
- Déploiement cloud de l'API avec supervision.

## 8. Planning

Rendu visé : **dimanche 1er novembre** (une journée d'avance sur l'échéance officielle).

| Date | Lot | Contenu |
|---|---|---|
| Sam 24 oct. | 1–2 | Cadrage, arbitrage, architecture, backlog, squelette du dépôt, CI au vert, téléchargement des données, début du MLD |
| Dim 25 oct. | 2 | MLD, schéma SQL, chargement des 9 CSV dans PostgreSQL, pipeline Prefect |
| Lun 26 oct. | 2 | Contrôles qualité, rapport avant/après, 8 requêtes SQL documentées |
| Mar 27 oct. | 3 | EDA, 2 tests statistiques, RFM, clustering, personas · point d'étape 1 |
| Mer 28 oct. | 3–4 | Dashboard Streamlit, modèle de retard de livraison |
| Jeu 29 oct. | 4 | Modèle de sentiment (baseline vs réseau de neurones), audit d'équité par région · point d'étape 2 |
| Ven 30 oct. | 5 | Endpoints API, tests, couverture, Docker, CI |
| Sam 31 oct. | — | Note éthique, rétro, README, test sur un clone propre, support et script de présentation |
| Dim 1er nov. | — | Tournage de la vidéo, vérification finale, rendu |
