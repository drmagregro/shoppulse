# Rétrospective — écarts avec la feuille de route

## Ce qui a été livré

| Lot | Livrables | Statut |
|---|---|---|
| 1 — Cadrage | Note de cadrage, arbitrages, architecture, backlog GitHub Projects | ✅ |
| 2 — Données | MLD, schémas raw / clean / mart, pipeline Prefect idempotent, rapport qualité, 8 requêtes SQL | ✅ |
| 3 — Analyse | EDA, 2 tests statistiques, segmentation RFM, 3 personas, 3 campagnes, dashboard Streamlit | ✅ |
| 4 — Modèles | Modèle de retard, modèle de sentiment, audit d'équité, note éthique | ✅ |
| 5 — Industrialisation | API FastAPI (2 endpoints), tests pytest, ruff, Docker, CI GitHub Actions | ✅ |

## Écarts avec le planning

- **Retard d'environ une journée (25-26 octobre)** sur la mise en place de la base : conflit avec un PostgreSQL déjà installé (port 5432 → 5433), mot de passe du `.env` modifié après la création du conteneur, prise en main de Prefect. Rattrapé le 27 octobre.
- **Requête de contrôle qualité bloquante** : un `NOT IN` sur un million de lignes figeait le pipeline ; remplacé par `NOT EXISTS` (moins d'une seconde).
- **Rendu avancé au 1er novembre** (au lieu du 2) pour une contrainte personnelle ; le planning a été recalé en conséquence, puis adapté à mes horaires de travail en semaine.

## Écarts techniques

- **Réseau de neurones** : `MLPClassifier` de scikit-learn au lieu de PyTorch. Plus léger à servir dans l'API et à tester dans la CI ; la comparaison avec la baseline reste valable. Le réseau n'apportant pas de gain (F1 macro 0,926 contre 0,925), la régression logistique a été retenue.
- **Dashboard** : Streamlit plutôt que Metabase, pour qu'il soit versionné avec le code.
- **Bonus** (MLflow, déploiement cloud, Spark) : non réalisés, priorité donnée au minimum de chaque lot.

## Ce que je referais autrement

- **Fixer le `.env` et les ports dès le premier jour** et vérifier qu'aucun autre service n'occupe le port de la base : cela aurait évité la journée de retard.
- **Valider le modèle de retard dans le temps** (entraîner sur 2017, tester sur 2018) plutôt qu'avec un découpage aléatoire, le mois d'achat étant la variable la plus importante.
- **Écrire les tests en même temps que le code**, et pas après, pour garder une couverture élevée sans effort en fin de projet.
- **Ouvrir les pull requests plus petites et plus tôt** : certaines branches ont regroupé plusieurs étapes.
