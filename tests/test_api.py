import pandas as pd
import pytest
from fastapi.testclient import TestClient
from sklearn.linear_model import LogisticRegression

from shoppulse.api import main
from shoppulse.models.delay import creer_pipeline
from shoppulse.models.sentiment import creer_baseline

client = TestClient(main.app)

AVIS = ["otimo produto recomendo", "excelente chegou rapido", "pessimo nao recebi",
        "nao recomendo defeito"] * 5
LABELS = [1, 1, 0, 0] * 5

COMMANDE = {
    "distance_km": 850.0,
    "delai_promis_jours": 24,
    "nb_articles": 1,
    "prix_total": 129.9,
    "frais_port": 18.5,
    "poids_total_g": 1200,
    "volume_cm3": 8000,
    "mois_achat": 11,
    "jour_semaine": 1,
    "nb_commandes_vendeur_avant": 35,
    "taux_retard_vendeur_avant": 0.12,
    "customer_state": "ba",
}


# Avant chaque test : on remplace les vrais modèles par de petits modèles entraînés
# sur des données inventées (pas besoin des fichiers .joblib ni de la base)
@pytest.fixture
def modeles_de_test():
    X = pd.DataFrame([dict(COMMANDE, distance_km=100 * i, customer_state="SP") for i in range(20)])
    y = [1 if i >= 15 else 0 for i in range(20)]
    main.modeles["retard"] = creer_pipeline(LogisticRegression()).fit(X, y)
    main.modeles["sentiment"] = creer_baseline().fit(AVIS, LABELS)
    yield
    main.modeles.clear()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "retard" in response.json()["modeles"]


def test_predict_delay(modeles_de_test):
    response = client.post("/predict/delay", json=COMMANDE)
    assert response.status_code == 200
    resultat = response.json()
    assert 0 <= resultat["probabilite_retard"] <= 1
    assert resultat["niveau_risque"] in ["faible", "moyen", "élevé"]


def test_predict_delay_sans_historique_vendeur(modeles_de_test):
    commande = dict(COMMANDE)
    del commande["taux_retard_vendeur_avant"]
    assert client.post("/predict/delay", json=commande).status_code == 200


def test_predict_delay_donnees_invalides(modeles_de_test):
    commande = dict(COMMANDE, mois_achat=13)
    assert client.post("/predict/delay", json=commande).status_code == 422


def test_predict_sentiment(modeles_de_test):
    response = client.post("/predict/sentiment", json={"texte": "Produto ótimo, recomendo!"})
    assert response.status_code == 200
    assert response.json()["sentiment"] in ["positif", "négatif"]


def test_predict_sentiment_texte_vide(modeles_de_test):
    assert client.post("/predict/sentiment", json={"texte": ""}).status_code == 422


def test_modele_absent_renvoie_503(monkeypatch):
    main.modeles.clear()
    monkeypatch.setitem(main.CHEMINS, "sentiment", "models/inexistant.joblib")
    response = client.post("/predict/sentiment", json={"texte": "bom"})
    assert response.status_code == 503
