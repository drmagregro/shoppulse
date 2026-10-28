import pandas as pd
from sklearn.linear_model import LogisticRegression

from shoppulse.models.delay import (
    VARIABLES_CATEGORIELLES,
    VARIABLES_NUMERIQUES,
    charger_modele,
    creer_pipeline,
    entrainer_et_sauvegarder,
    predire_retard,
)


# Petit jeu de données inventé pour tester sans base de données
def faux_jeu_de_donnees():
    lignes = []
    for i in range(40):
        lignes.append({
            "distance_km": 100 + i * 50,
            "delai_promis_jours": 20,
            "nb_articles": 1,
            "prix_total": 100.0,
            "frais_port": 15.0,
            "poids_total_g": 500,
            "volume_cm3": 3000,
            "mois_achat": 5,
            "jour_semaine": 2,
            "nb_commandes_vendeur_avant": i,
            "taux_retard_vendeur_avant": None if i == 0 else 0.1,
            "customer_state": "SP" if i % 2 == 0 else "AL",
        })
    X = pd.DataFrame(lignes)
    y = [1 if i >= 30 else 0 for i in range(40)]  # les commandes lointaines sont en retard
    return X, y


def test_les_variables_sont_definies():
    assert len(VARIABLES_NUMERIQUES) >= 5
    assert "customer_state" in VARIABLES_CATEGORIELLES


def test_le_pipeline_predit_une_probabilite():
    X, y = faux_jeu_de_donnees()
    pipeline = creer_pipeline(LogisticRegression())
    pipeline.fit(X, y)
    proba = predire_retard(pipeline, X.iloc[0].to_dict())
    assert 0 <= proba <= 1


def test_un_etat_inconnu_ne_fait_pas_planter():
    X, y = faux_jeu_de_donnees()
    pipeline = creer_pipeline(LogisticRegression())
    pipeline.fit(X, y)
    commande = X.iloc[0].to_dict()
    commande["customer_state"] = "XX"
    assert 0 <= predire_retard(pipeline, commande) <= 1


def test_sauvegarde_et_rechargement(tmp_path):
    X, y = faux_jeu_de_donnees()
    chemin = tmp_path / "modele.joblib"
    entrainer_et_sauvegarder(LogisticRegression(), X, y, chemin=chemin)
    modele = charger_modele(chemin)
    assert 0 <= predire_retard(modele, X.iloc[5].to_dict()) <= 1
