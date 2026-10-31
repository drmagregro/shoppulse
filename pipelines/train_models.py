# Entraîne les deux modèles finaux et les enregistre dans models/
# (mêmes réglages que dans les notebooks 03_modele_retard et 04_sentiment)
# Prérequis : la base est remplie par pipelines/etl_flow.py
# Lancement : python pipelines/train_models.py

import os

from sklearn.ensemble import RandomForestClassifier
from sqlalchemy import create_engine

from shoppulse.config import settings
from shoppulse.models import delay, sentiment

engine = create_engine(settings.database_url)
os.makedirs("models", exist_ok=True)

# Modèle de retard : Random Forest
print("Entraînement du modèle de retard...")
X, y = delay.charger_donnees(engine)
foret = RandomForestClassifier(
    n_estimators=100, max_depth=12, class_weight="balanced", n_jobs=-1, random_state=42
)
delay.entrainer_et_sauvegarder(foret, X, y)

# Modèle de sentiment : TF-IDF + régression logistique
print("Entraînement du modèle de sentiment...")
X, y = sentiment.charger_donnees(engine)
sentiment.entrainer_et_sauvegarder(sentiment.creer_baseline(), X, y)

print("Terminé : les deux modèles sont dans models/")
