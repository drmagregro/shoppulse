from shoppulse.etl.quality import CONTROLES, ligne_markdown


# Le rapport doit contenir au moins 10 contrôles
def test_au_moins_10_controles():
    assert len(CONTROLES) >= 10


# Chaque contrôle compare raw (avant) et clean (après)
def test_chaque_controle_compare_raw_et_clean():
    for controle in CONTROLES:
        sql_avant = controle[1]
        sql_apres = controle[2]
        assert "raw" in sql_avant
        assert "clean" in sql_apres


# Les grands nombres sont lisibles (espace entre les milliers)
def test_ligne_markdown():
    ligne = ligne_markdown("Test", 1000163, 19015, "ok")
    assert ligne == "| Test | 1 000 163 | 19 015 | ok |"
