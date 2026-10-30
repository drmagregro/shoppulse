"""API FastAPI de ShopPulse : un endpoint par modèle.

Lancement local : uvicorn shoppulse.api.main:app --reload
Documentation : http://localhost:8000/docs
"""

import os

import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from shoppulse import __version__
from shoppulse.models.delay import CHEMIN_MODELE as CHEMIN_RETARD
from shoppulse.models.delay import predire_retard
from shoppulse.models.sentiment import CHEMIN_MODELE as CHEMIN_SENTIMENT
from shoppulse.models.sentiment import predire_sentiment

app = FastAPI(
    title="ShopPulse API",
    description="Prédiction du retard de livraison et du sentiment des avis.",
    version=__version__,
)

# Les modèles sont chargés au premier appel, puis gardés en mémoire
CHEMINS = {"retard": CHEMIN_RETARD, "sentiment": CHEMIN_SENTIMENT}
modeles = {}


def get_modele(nom: str):
    if nom not in modeles:
        chemin = CHEMINS[nom]
        if not os.path.exists(chemin):
            message = f"Modèle '{nom}' introuvable ({chemin}) : lancer son notebook"
            raise HTTPException(status_code=503, detail=message)
        modeles[nom] = joblib.load(chemin)
    return modeles[nom]


# ---------- Schémas d'entrée et de sortie ----------
class Commande(BaseModel):
    """Informations connues au moment de l'achat."""

    distance_km: float = Field(ge=0, examples=[850.0])
    delai_promis_jours: float = Field(ge=0, examples=[24])
    nb_articles: int = Field(ge=1, examples=[1])
    prix_total: float = Field(ge=0, examples=[129.9])
    frais_port: float = Field(ge=0, examples=[18.5])
    poids_total_g: float = Field(ge=0, examples=[1200])
    volume_cm3: float = Field(ge=0, examples=[8000])
    mois_achat: int = Field(ge=1, le=12, examples=[11])
    jour_semaine: int = Field(ge=1, le=7, examples=[1])
    nb_commandes_vendeur_avant: int = Field(ge=0, examples=[35])
    taux_retard_vendeur_avant: float | None = Field(default=None, ge=0, le=1, examples=[0.12])
    customer_state: str = Field(min_length=2, max_length=2, examples=["BA"])


class PredictionRetard(BaseModel):
    probabilite_retard: float
    en_retard: bool
    niveau_risque: str


class Avis(BaseModel):
    texte: str = Field(min_length=1, examples=["Não recebi o produto, péssimo."])


class PredictionSentiment(BaseModel):
    sentiment: str
    probabilite_positif: float


# ---------- Endpoints ----------
@app.get("/health", tags=["monitoring"])
def health() -> dict:
    """Vérifie que l'API répond et indique les modèles disponibles."""
    disponibles = {nom: os.path.exists(chemin) for nom, chemin in CHEMINS.items()}
    return {"status": "ok", "version": __version__, "modeles": disponibles}


@app.post("/predict/delay", response_model=PredictionRetard, tags=["modèles"])
def predict_delay(commande: Commande) -> PredictionRetard:
    """Probabilité qu'une commande soit livrée après la date promise."""
    donnees = commande.model_dump()
    donnees["customer_state"] = donnees["customer_state"].upper()
    proba = predire_retard(get_modele("retard"), donnees)

    if proba >= 0.7:
        niveau = "élevé"
    elif proba >= 0.5:
        niveau = "moyen"
    else:
        niveau = "faible"
    return PredictionRetard(
        probabilite_retard=round(proba, 3), en_retard=proba >= 0.5, niveau_risque=niveau
    )


@app.post("/predict/sentiment", response_model=PredictionSentiment, tags=["modèles"])
def predict_sentiment(avis: Avis) -> PredictionSentiment:
    """Sentiment (positif ou négatif) d'un avis client écrit en portugais."""
    return PredictionSentiment(**predire_sentiment(get_modele("sentiment"), avis.texte))
