# Modèle de prédiction du retard de livraison
# Utilisé par le notebook 03_modele_retard.ipynb (entraînement) et par l'API (prédiction)

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# Variables connues au moment de l'achat
VARIABLES_NUMERIQUES = [
    "distance_km",
    "delai_promis_jours",
    "nb_articles",
    "prix_total",
    "frais_port",
    "poids_total_g",
    "volume_cm3",
    "mois_achat",
    "jour_semaine",
    "nb_commandes_vendeur_avant",
    "taux_retard_vendeur_avant",
]
VARIABLES_CATEGORIELLES = ["customer_state"]
CIBLE = "en_retard"

CHEMIN_MODELE = "models/modele_retard.joblib"


# Lit la table de features calculée par le pipeline
def charger_donnees(engine):
    df = pd.read_sql("SELECT * FROM mart.features_retard", engine)
    X = df[VARIABLES_NUMERIQUES + VARIABLES_CATEGORIELLES]
    y = df[CIBLE]
    return X, y


# Préparation des données + modèle, dans un seul objet
# - valeurs manquantes remplacées par la médiane (ex : vendeur sans historique)
# - variables numériques standardisées
# - état du client transformé en colonnes 0/1 (one-hot)
def creer_pipeline(modele):
    numerique = Pipeline([
        ("valeurs_manquantes", SimpleImputer(strategy="median")),
        ("standardisation", StandardScaler()),
    ])
    preparation = ColumnTransformer([
        ("num", numerique, VARIABLES_NUMERIQUES),
        ("cat", OneHotEncoder(handle_unknown="ignore"), VARIABLES_CATEGORIELLES),
    ])
    return Pipeline([("preparation", preparation), ("modele", modele)])


# Entraîne le modèle sur toutes les données et l'enregistre dans models/
def entrainer_et_sauvegarder(modele, X, y, chemin=CHEMIN_MODELE):
    pipeline = creer_pipeline(modele)
    pipeline.fit(X, y)
    joblib.dump(pipeline, chemin)
    print(f"Modèle enregistré dans {chemin}")
    return pipeline


# Charge le modèle enregistré
def charger_modele(chemin=CHEMIN_MODELE):
    return joblib.load(chemin)


# Probabilité de retard pour une commande (dictionnaire avec les variables)
def predire_retard(pipeline, commande):
    X = pd.DataFrame([commande])[VARIABLES_NUMERIQUES + VARIABLES_CATEGORIELLES]
    return float(pipeline.predict_proba(X)[0, 1])
