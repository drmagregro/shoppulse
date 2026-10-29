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


-- ---------- FEATURES DU MODÈLE DE RETARD ----------
-- Une ligne par commande livrée. Uniquement des informations connues au moment
-- de l'achat (pas de date de livraison réelle dans les variables explicatives).
-- Cible : en_retard = 1 si la commande est livrée après la date estimée.
DROP TABLE IF EXISTS mart.features_retard;
CREATE TABLE mart.features_retard AS
WITH vendeur_principal AS (
    -- Le vendeur du premier article de la commande
    SELECT order_id, seller_id
    FROM clean.order_items
    WHERE order_item_id = 1
),
colis AS (
    SELECT
        i.order_id,
        COUNT(*)                                                         AS nb_articles,
        SUM(i.price)                                                     AS prix_total,
        SUM(i.freight_value)                                             AS frais_port,
        SUM(p.product_weight_g)                                          AS poids_total_g,
        SUM(p.product_length_cm * p.product_height_cm * p.product_width_cm) AS volume_cm3
    FROM clean.order_items i
    JOIN clean.products p ON p.product_id = i.product_id
    GROUP BY i.order_id
),
commandes AS (
    SELECT
        o.order_id,
        o.order_purchase_timestamp,
        c.customer_state,
        v.seller_id,
        gc.geolocation_lat AS lat_client,
        gc.geolocation_lng AS lng_client,
        gv.geolocation_lat AS lat_vendeur,
        gv.geolocation_lng AS lng_vendeur,
        EXTRACT(DAY FROM o.order_estimated_delivery_date - o.order_purchase_timestamp)
                                                   AS delai_promis_jours,
        CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date
             THEN 1 ELSE 0 END                     AS en_retard
    FROM clean.orders o
    JOIN clean.customers c          ON c.customer_id = o.customer_id
    JOIN vendeur_principal v        ON v.order_id = o.order_id
    JOIN clean.sellers s            ON s.seller_id = v.seller_id
    LEFT JOIN clean.geolocation gc  ON gc.geolocation_zip_code_prefix = c.customer_zip_code_prefix
    LEFT JOIN clean.geolocation gv  ON gv.geolocation_zip_code_prefix = s.seller_zip_code_prefix
    WHERE o.order_status = 'delivered'
      AND o.order_delivered_customer_date IS NOT NULL
)
SELECT
    cm.order_id,
    cm.order_purchase_timestamp,
    cm.customer_state,
    -- Distance à vol d'oiseau entre le client et le vendeur (formule de haversine, en km)
    ROUND((6371 * 2 * ASIN(SQRT(
        POWER(SIN(RADIANS(cm.lat_client - cm.lat_vendeur) / 2), 2)
        + COS(RADIANS(cm.lat_vendeur)) * COS(RADIANS(cm.lat_client))
        * POWER(SIN(RADIANS(cm.lng_client - cm.lng_vendeur) / 2), 2)
    )))::NUMERIC, 1)                                           AS distance_km,
    cm.delai_promis_jours,
    co.nb_articles,
    co.prix_total,
    co.frais_port,
    co.poids_total_g,
    co.volume_cm3,
    EXTRACT(MONTH FROM cm.order_purchase_timestamp)            AS mois_achat,
    EXTRACT(ISODOW FROM cm.order_purchase_timestamp)           AS jour_semaine,
    -- Historique du vendeur : seulement ses commandes PASSÉES (fonction de fenêtre)
    COUNT(*) OVER (
        PARTITION BY cm.seller_id ORDER BY cm.order_purchase_timestamp
        ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
    )                                                          AS nb_commandes_vendeur_avant,
    AVG(cm.en_retard) OVER (
        PARTITION BY cm.seller_id ORDER BY cm.order_purchase_timestamp
        ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
    )                                                          AS taux_retard_vendeur_avant,
    cm.en_retard
FROM commandes cm
JOIN colis co ON co.order_id = cm.order_id;

ALTER TABLE mart.features_retard ADD PRIMARY KEY (order_id);


-- ---------- AVIS POUR LE MODÈLE DE SENTIMENT ----------
-- Un avis avec un commentaire écrit (titre et/ou message), en portugais.
-- Label dérivé de la note : 1-2 = négatif (0), 4-5 = positif (1).
-- Les notes de 3 sont exclues : elles sont ambiguës (ni vraiment positives, ni négatives).
DROP TABLE IF EXISTS mart.avis_sentiment;
CREATE TABLE mart.avis_sentiment AS
SELECT
    review_id,
    order_id,
    TRIM(CONCAT_WS(' ', review_comment_title, review_comment_message)) AS texte,
    review_score                                                      AS note,
    CASE WHEN review_score >= 4 THEN 1 ELSE 0 END                     AS positif
FROM clean.order_reviews
WHERE review_score <> 3
  AND (review_comment_title IS NOT NULL OR review_comment_message IS NOT NULL)
  AND TRIM(CONCAT_WS(' ', review_comment_title, review_comment_message)) <> '';

ALTER TABLE mart.avis_sentiment ADD PRIMARY KEY (review_id, order_id);
