# Note éthique — ShopPulse

## 1. Données personnelles (RGPD)

- **Données traitées** : identifiants clients et vendeurs (pseudonymisés par Olist), villes, états, codes postaux (5 premiers chiffres), avis écrits.
- **Minimisation** : aucun nom, e-mail, adresse complète ni moyen de paiement nominatif. Les analyses se font à la maille de l'état ou de la région, jamais à l'échelle d'une adresse.
- **Avis clients** : les textes peuvent contenir des informations personnelles saisies librement. Ils servent uniquement à entraîner le modèle de sentiment et ne sont pas exposés par l'API, qui ne renvoie que le sentiment prédit.
- **Stockage** : les données complètes restent dans `data/raw/` (non versionné) et dans la base PostgreSQL locale. Le dépôt ne contient que du code, de la documentation et des échantillons de moins de 1 Mo. Aucun secret n'est versionné (`.env` ignoré, seul `.env.example` est publié).
- **En production** : il faudrait une base légale (intérêt légitime pour la logistique, information des clients sur l'usage de leurs avis), une durée de conservation limitée et un contrôle des accès à la base.

## 2. Biais et équité du modèle de retard

L'audit (`notebooks/05_audit_equite.ipynb`) compare le modèle sur les 5 grandes régions du Brésil :

- **Rappel** : les retards du Nordeste sont **mieux** détectés (78 %) que ceux du Sudeste et du Sul (environ 50 %). Les clients les plus exposés aux retards ne sont pas désavantagés.
- **Précision** : homogène (17 % à 24 % selon la région).
- **Fausses alertes** : **43 %** des commandes à l'heure du Nordeste sont signalées, contre **12 %** dans le Sudeste. Le modèle s'appuie sur l'état du client et la distance : il « soupçonne » davantage certaines régions.

**Règle d'usage retenue** : le score de retard ne doit servir qu'à des **actions favorables** au client (le prévenir, prioriser l'expédition, choisir un meilleur transporteur). Il ne doit **jamais** servir à le pénaliser (frais de port majorés, délai rallongé, refus de vente), ce qui reviendrait à une discrimination géographique.

## 3. Transparence et limites des modèles

- **Modèle de retard** : détecte 55 % des retards ; environ 1 alerte sur 4 est justifiée. Le mois d'achat est la variable la plus importante, ce qui limite la généralisation à d'autres années.
- **Modèle de sentiment** : 94 % des avis négatifs détectés, mais il comprend mal les avis nuancés (« o produto é bom mas a entrega atrasou »). Une décision importante concernant un client ne doit pas reposer sur ce seul score.
- **Contrôle humain** : les deux modèles sont des **aides à la décision**. Les équipes logistique et service client gardent la décision finale.

## 4. Suivi recommandé

- Recalculer les métriques **par région** à chaque réentraînement (même tableau que l'audit).
- Surveiller la dérive des données (nouvelles périodes, nouveaux vendeurs) et réentraîner régulièrement.
- Tester un modèle de retard **sans l'état du client** (en gardant la distance) et comparer son équité.
- Documenter tout changement de seuil de décision et son impact par région.
