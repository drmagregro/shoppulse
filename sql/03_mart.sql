-- =====================================================================
-- Schéma MART : tables prêtes pour l'analyse, calculées à partir de clean
-- Rejouable : chaque table est supprimée puis recréée.
-- =====================================================================

CREATE SCHEMA IF NOT EXISTS mart;


-- ---------- RFM (Récence, Fréquence, Montant) ----------
-- Une ligne par client réel (customer_unique_id), commandes livrées uniquement.
-- Récence : nombre de jours depuis la dernière commande, par rapport au
-- lendemain de la dernière commande du dataset (les données s'arrêtent en 2018).
DROP TABLE IF EXISTS mart.rfm;
CREATE TABLE mart.rfm AS
WITH commandes AS (
    SELECT
        c.customer_unique_id,
        o.order_id,
        o.order_purchase_timestamp,
        SUM(i.price + i.freight_value) AS montant_commande
    FROM clean.orders o
    JOIN clean.customers c   ON c.customer_id = o.customer_id
    JOIN clean.order_items i ON i.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id, o.order_id, o.order_purchase_timestamp
),
date_reference AS (
    SELECT MAX(order_purchase_timestamp) + INTERVAL '1 day' AS date_ref
    FROM commandes
),
rfm AS (
    SELECT
        customer_unique_id,
        EXTRACT(DAY FROM (SELECT date_ref FROM date_reference) - MAX(order_purchase_timestamp))::INTEGER
                                        AS recence_jours,
        COUNT(*)                        AS frequence,
        ROUND(SUM(montant_commande)::NUMERIC, 2) AS montant
    FROM commandes
    GROUP BY customer_unique_id
)
SELECT
    customer_unique_id,
    recence_jours,
    frequence,
    montant,
    -- Scores de 1 à 5 (5 = meilleur) avec la fonction de fenêtre NTILE
    NTILE(5) OVER (ORDER BY recence_jours DESC) AS score_r,
    NTILE(5) OVER (ORDER BY montant)            AS score_m
FROM rfm;

ALTER TABLE mart.rfm ADD PRIMARY KEY (customer_unique_id);
