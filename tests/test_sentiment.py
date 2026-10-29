from shoppulse.models.sentiment import (
    MOTS_VIDES,
    charger_modele,
    creer_baseline,
    creer_reseau_neurones,
    entrainer_et_sauvegarder,
    nettoyer_texte,
    predire_sentiment,
)

# Petit jeu d'avis inventés pour tester sans base de données
AVIS = [
    "produto otimo chegou rapido", "excelente qualidade recomendo", "adorei muito bom",
    "entrega no prazo gostei", "muito bom recomendo a todos", "perfeito chegou antes",
    "nao recebi o produto", "pessimo atrasou muito", "produto com defeito horrivel",
    "nao recomendo demorou demais", "veio quebrado pessimo", "nunca chegou nao gostei",
] * 3
LABELS = [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0] * 3


def test_nettoyer_texte():
    assert nettoyer_texte("Ótimo produto!! Chegou em 2 dias") == "otimo produto chegou em dias"


def test_la_negation_est_gardee():
    assert "nao" not in MOTS_VIDES


def test_baseline_predit_un_sentiment():
    modele = creer_baseline().fit(AVIS, LABELS)
    resultat = predire_sentiment(modele, "Produto ótimo, recomendo!")
    assert resultat["sentiment"] in ["positif", "négatif"]
    assert 0 <= resultat["probabilite_positif"] <= 1


def test_reseau_neurones_s_entraine():
    modele = creer_reseau_neurones()
    modele.set_params(modele__early_stopping=False, tfidf__min_df=1)
    modele.fit(AVIS, LABELS)
    assert predire_sentiment(modele, "pessimo nao recebi")["sentiment"] in ["positif", "négatif"]


def test_sauvegarde_et_rechargement(tmp_path):
    chemin = tmp_path / "sentiment.joblib"
    entrainer_et_sauvegarder(creer_baseline(), AVIS, LABELS, chemin=chemin)
    modele = charger_modele(chemin)
    assert predire_sentiment(modele, "excelente")["sentiment"] in ["positif", "négatif"]
