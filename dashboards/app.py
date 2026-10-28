# Dashboard direction ShopPulse
# Lancement : python -m streamlit run dashboards/app.py

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

from shoppulse.config import settings

st.set_page_config(page_title="ShopPulse", layout="wide")
engine = create_engine(settings.database_url)


def lire(requete):
    return pd.read_sql(requete, engine)


st.title("ShopPulse - Dashboard direction")
st.write("Commandes livrées (schéma clean)")

# Filtre sur l'année
annee = st.sidebar.selectbox("Année", ["Toutes", "2017", "2018"])
if annee == "Toutes":
    filtre = ""
else:
    filtre = f"AND EXTRACT(YEAR FROM o.order_purchase_timestamp) = {int(annee)}"


# KPI 1, 2 et 3 : chiffre d'affaires, nombre de commandes, panier moyen
ventes = lire(f"""
    SELECT COUNT(DISTINCT o.order_id) AS nb_commandes,
           SUM(i.price) AS ca
    FROM clean.orders o
    JOIN clean.order_items i ON i.order_id = o.order_id
    WHERE o.order_status = 'delivered' {filtre}
""")
nb_commandes = ventes["nb_commandes"][0]
ca = ventes["ca"][0]
panier_moyen = ca / nb_commandes

# KPI 4 et 5 : taux de retard et note moyenne
livraisons = lire(f"""
    SELECT o.order_delivered_customer_date > o.order_estimated_delivery_date AS en_retard,
           r.review_score
    FROM clean.orders o
    LEFT JOIN clean.order_reviews r ON r.order_id = o.order_id
    WHERE o.order_status = 'delivered'
      AND o.order_delivered_customer_date IS NOT NULL {filtre}
""")
taux_retard = livraisons["en_retard"].mean() * 100
note_moyenne = livraisons["review_score"].mean()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Chiffre d'affaires", f"{ca / 1000000:.2f} M R$")
col2.metric("Commandes", nb_commandes)
col3.metric("Panier moyen", f"{panier_moyen:.0f} R$")
col4.metric("Taux de retard", f"{taux_retard:.1f} %")
col5.metric("Note moyenne", f"{note_moyenne:.2f} / 5")


# Graphique 1 : chiffre d'affaires par mois
st.subheader("Chiffre d'affaires par mois")
ca_mois = lire(f"""
    SELECT DATE_TRUNC('month', o.order_purchase_timestamp) AS mois,
           SUM(i.price) AS ca
    FROM clean.orders o
    JOIN clean.order_items i ON i.order_id = o.order_id
    WHERE o.order_status = 'delivered' {filtre}
    GROUP BY mois
    ORDER BY mois
""")
st.line_chart(ca_mois, x="mois", y="ca")


# Graphique 2 : taux de retard par état
st.subheader("Taux de retard par état (%)")
retards = lire(f"""
    SELECT c.customer_state AS etat,
           o.order_delivered_customer_date > o.order_estimated_delivery_date AS en_retard
    FROM clean.orders o
    JOIN clean.customers c ON c.customer_id = o.customer_id
    WHERE o.order_status = 'delivered'
      AND o.order_delivered_customer_date IS NOT NULL {filtre}
""")
par_etat = retards.groupby("etat")["en_retard"].agg(["mean", "count"])
par_etat = par_etat[par_etat["count"] >= 100]  # on enlève les états avec trop peu de commandes
par_etat["taux_retard"] = par_etat["mean"] * 100
par_etat = par_etat.reset_index()
# sort="-taux_retard" : barres triées du plus fort au plus faible taux de retard
st.bar_chart(par_etat, x="etat", y="taux_retard", sort="-taux_retard")


# Graphique 3 : note moyenne selon le retard
st.subheader("Note moyenne : en retard ou à l'heure")
notes = livraisons.dropna(subset=["review_score"])
notes["livraison"] = notes["en_retard"].map({True: "En retard", False: "À l'heure"})
st.bar_chart(notes.groupby("livraison")["review_score"].mean())
