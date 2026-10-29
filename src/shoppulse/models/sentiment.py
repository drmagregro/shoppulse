# Modèle d'analyse de sentiment des avis clients (en portugais)
# Utilisé par le notebook 04_sentiment.ipynb (entraînement) et par l'API (prédiction)

import re
import unicodedata

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline

CHEMIN_MODELE = "models/modele_sentiment.joblib"

# Mots très fréquents en portugais qui n'apportent pas de sens.
# On garde volontairement "nao" (ne pas) : la négation change le sens d'un avis.
MOTS_VIDES = [
    "a", "o", "as", "os", "de", "da", "do", "das", "dos", "e", "em", "no", "na",
    "nos", "nas", "um", "uma", "para", "pra", "com", "por", "que", "se", "ao",
    "eu", "me", "meu", "minha", "ele", "ela", "foi", "ja", "ser", "esta", "isso",
]


# Met le texte en minuscules, enlève les accents, les chiffres et la ponctuation
# Exemple : "Ótimo produto!! Chegou em 2 dias" -> "otimo produto chegou em dias"
def nettoyer_texte(texte):
    texte = str(texte).lower()
    texte = unicodedata.normalize("NFKD", texte)
    texte = "".join(c for c in texte if not unicodedata.combining(c))
    texte = re.sub(r"[^a-z ]", " ", texte)
    return re.sub(r"\s+", " ", texte).strip()


# Lit les avis calculés par le pipeline
def charger_donnees(engine):
    df = pd.read_sql("SELECT texte, positif FROM mart.avis_sentiment", engine)
    X = df["texte"].apply(nettoyer_texte)
    y = df["positif"]
    return X, y


# Modèle 1 (baseline) : TF-IDF + régression logistique
# TF-IDF transforme chaque avis en vecteur : un poids par mot (ou paire de mots),
# élevé si le mot est fréquent dans l'avis mais rare dans l'ensemble des avis.
def creer_baseline():
    return Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=3, stop_words=MOTS_VIDES)),
        ("modele", LogisticRegression(class_weight="balanced", max_iter=1000)),
    ])


# Modèle 2 : TF-IDF + réseau de neurones (perceptron multicouche)
# Une couche cachée de 64 neurones ; early_stopping arrête l'entraînement
# quand le score ne progresse plus sur une partie des données (évite le surapprentissage).
def creer_reseau_neurones():
    return Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=3, max_features=20000,
                                  stop_words=MOTS_VIDES)),
        ("modele", MLPClassifier(hidden_layer_sizes=(64,), early_stopping=True,
                                 max_iter=50, random_state=42)),
    ])


# Entraîne le modèle sur toutes les données et l'enregistre dans models/
def entrainer_et_sauvegarder(pipeline, X, y, chemin=CHEMIN_MODELE):
    pipeline.fit(X, y)
    joblib.dump(pipeline, chemin)
    print(f"Modèle enregistré dans {chemin}")
    return pipeline


# Charge le modèle enregistré
def charger_modele(chemin=CHEMIN_MODELE):
    return joblib.load(chemin)


# Sentiment d'un avis : "positif" ou "négatif", avec la probabilité d'être positif
def predire_sentiment(pipeline, texte):
    proba = float(pipeline.predict_proba([nettoyer_texte(texte)])[0, 1])
    sentiment = "positif" if proba >= 0.5 else "négatif"
    return {"sentiment": sentiment, "probabilite_positif": round(proba, 3)}
