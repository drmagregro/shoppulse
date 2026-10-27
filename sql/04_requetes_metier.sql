-- =====================================================================
-- 8 requêtes métier ShopPulse (schéma clean)
-- Chiffre d'affaires (CA) = somme des prix des articles des commandes livrées.
-- =====================================================================


-- Q1 — Chiffre d'affaires par mois
-- Objectif : suivre la saisonnalité des ventes (KPI direction)
-- Techniques : jointure, agrégat (SUM), regroupement par mois
-- Résultat : le CA passe de 112 k R$ (janvier 2017) à 850-980 k R$ par mois en 2018.
--            Pic en novembre 2017 (988 k R$, Black Friday). 2016 est quasi vide (lancement).
SELECT
    DATE_TRUNC('month', o.order_purchase_timestamp) AS mois,
    ROUND(SUM(i.price), 2)                          AS chiffre_affaires
FROM clean.orders o
JOIN clean.order_items i ON i.order_id = o.order_id
WHERE o.order_status = 'delivered'
GROUP BY mois
ORDER BY mois;


-- Q2 — Top 10 des catégories par chiffre d'affaires
-- Objectif : savoir quelles catégories font vivre la marketplace (marketing)
-- Techniques : jointure multiple (3 tables), agrégat, COALESCE pour les catégories inconnues
-- Résultat : health_beauty en tête (1,26 M R$), devant watches_gifts (1,21 M R$)
--            et bed_bath_table (1,04 M R$), catégorie la plus vendue en volume (11 115 articles).
SELECT
    COALESCE(t.product_category_name_english, p.product_category_name, 'inconnue') AS categorie,
    COUNT(*)                AS nb_articles_vendus,
    ROUND(SUM(i.price), 2)  AS chiffre_affaires
FROM clean.order_items i
JOIN clean.products p ON p.product_id = i.product_id
LEFT JOIN clean.product_category_name_translation t
    ON t.product_category_name = p.product_category_name
GROUP BY categorie
ORDER BY chiffre_affaires DESC
LIMIT 10;


-- Q3 — Taux de retard de livraison par état du client
-- Objectif : repérer les régions où la logistique a le plus de difficultés
-- Techniques : jointure, CASE WHEN, agrégat, HAVING
-- Retard = livrée après la date estimée annoncée au client
-- Résultat : les états du Nord-Est sont les plus touchés (AL 23,9 %, MA 19,7 %, PI 16,0 %)
--            alors que SP, le plus gros marché (40 494 commandes), n'a que 5,9 % de retards.
SELECT
    c.customer_state AS etat,
    COUNT(*)         AS nb_commandes_livrees,
    ROUND(
        100.0 * SUM(CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date
                         THEN 1 ELSE 0 END) / COUNT(*),
        1
    ) AS taux_retard_pct
FROM clean.orders o
JOIN clean.customers c ON c.customer_id = o.customer_id
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
GROUP BY c.customer_state
HAVING COUNT(*) >= 100
ORDER BY taux_retard_pct DESC;


-- Q4 — Note moyenne des avis : commandes en retard vs à l'heure
-- Objectif : mesurer l'impact des retards sur la satisfaction (service client)
-- Techniques : jointure, CASE WHEN, agrégat
-- Résultat : 2,57/5 pour les commandes en retard contre 4,29/5 à l'heure (7 700 vs 88 653 avis).
--            Un retard fait perdre 1,7 point de note : il faut anticiper les retards.
SELECT
    CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date
         THEN 'en retard' ELSE 'à l''heure' END  AS livraison,
    COUNT(*)                                     AS nb_avis,
    ROUND(AVG(r.review_score), 2)                AS note_moyenne
FROM clean.orders o
JOIN clean.order_reviews r ON r.order_id = o.order_id
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
GROUP BY livraison;


-- Q5 — Panier moyen par mode de paiement
-- Objectif : connaître les habitudes de paiement des clients
-- Techniques : agrégats (COUNT, AVG, SUM)
-- Résultat : la carte de crédit domine (76 505 commandes, 163 R$ en moyenne, 3,5 mensualités),
--            devant le boleto (19 784 commandes, 145 R$).
SELECT
    payment_type                    AS mode_paiement,
    COUNT(DISTINCT order_id)        AS nb_commandes,
    ROUND(AVG(payment_value), 2)    AS montant_moyen,
    ROUND(AVG(payment_installments), 1) AS nb_moyen_mensualites
FROM clean.order_payments
GROUP BY payment_type
ORDER BY nb_commandes DESC;


-- Q6 — Classement des 10 meilleurs vendeurs par chiffre d'affaires
-- Objectif : identifier les vendeurs clés à fidéliser
-- Techniques : jointure, agrégat, fonction de fenêtre RANK()
-- Résultat : le 1er vendeur réalise 229 k R$. 9 des 10 meilleurs vendeurs sont basés à SP.
SELECT
    RANK() OVER (ORDER BY SUM(i.price) DESC) AS rang,
    i.seller_id,
    s.seller_state                           AS etat_vendeur,
    COUNT(DISTINCT i.order_id)               AS nb_commandes,
    ROUND(SUM(i.price), 2)                   AS chiffre_affaires
FROM clean.order_items i
JOIN clean.sellers s ON s.seller_id = i.seller_id
GROUP BY i.seller_id, s.seller_state
ORDER BY rang
LIMIT 10;


-- Q7 — Croissance du chiffre d'affaires par rapport au mois précédent
-- Objectif : voir si l'activité accélère ou ralentit (direction)
-- Techniques : sous-requête (CTE), fonction de fenêtre LAG()
-- On part de janvier 2017 : en 2016 il n'y a presque aucune commande (lancement),
-- ce qui donnerait des pourcentages de croissance sans signification.
-- Résultat : +52,4 % en novembre 2017 (Black Friday) puis -26,5 % en décembre.
--            En 2018 la croissance ralentit : le CA se stabilise entre 830 et 980 k R$ par mois.
WITH ca_mensuel AS (
    SELECT
        DATE_TRUNC('month', o.order_purchase_timestamp) AS mois,
        SUM(i.price)                                    AS chiffre_affaires
    FROM clean.orders o
    JOIN clean.order_items i ON i.order_id = o.order_id
    WHERE o.order_status = 'delivered'
      AND o.order_purchase_timestamp >= '2017-01-01'
    GROUP BY mois
)
SELECT
    mois,
    ROUND(chiffre_affaires, 2)                         AS chiffre_affaires,
    ROUND(LAG(chiffre_affaires) OVER (ORDER BY mois), 2) AS ca_mois_precedent,
    ROUND(
        100.0 * (chiffre_affaires - LAG(chiffre_affaires) OVER (ORDER BY mois))
        / LAG(chiffre_affaires) OVER (ORDER BY mois),
        1
    ) AS croissance_pct
FROM ca_mensuel
ORDER BY mois;


-- Q8 — Part des clients qui ont commandé plus d'une fois
-- Objectif : mesurer la fidélité / le réachat (marketing)
-- Techniques : CTE, agrégat, CASE WHEN
-- Attention : on compte par customer_unique_id (le vrai client),
-- car customer_id change à chaque commande.
-- Résultat : seulement 3,12 % des clients ont commandé plus d'une fois (2 997 sur 96 096).
--            Le réachat est très faible : c'est le premier levier pour le marketing.
WITH commandes_par_client AS (
    SELECT
        c.customer_unique_id,
        COUNT(o.order_id) AS nb_commandes
    FROM clean.customers c
    JOIN clean.orders o ON o.customer_id = c.customer_id
    GROUP BY c.customer_unique_id
)
SELECT
    COUNT(*)                                                    AS nb_clients,
    SUM(CASE WHEN nb_commandes > 1 THEN 1 ELSE 0 END)           AS nb_clients_fideles,
    ROUND(100.0 * SUM(CASE WHEN nb_commandes > 1 THEN 1 ELSE 0 END) / COUNT(*), 2)
                                                                AS part_fideles_pct
FROM commandes_par_client;
