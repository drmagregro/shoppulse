# Données

Les données complètes ne sont **jamais** versionnées (voir `.gitignore`).
Seuls des échantillons de moins de 1 Mo, produits par le pipeline, vont dans `data/sample/`.

## Télécharger le dataset Olist

Source : [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (Kaggle).

Option 1, avec l'API Kaggle (jeton dans `~/.kaggle/kaggle.json`) :

```bash
pip install kaggle
kaggle datasets download -d olistbr/brazilian-ecommerce -p data/raw --unzip
```

Option 2, à la main : télécharger le zip depuis la page Kaggle et le décompresser dans `data/raw/`.

## Fichiers attendus dans `data/raw/`

| Fichier | Contenu |
|---|---|
| olist_customers_dataset.csv | clients |
| olist_geolocation_dataset.csv | géolocalisation par code postal |
| olist_order_items_dataset.csv | lignes de commande |
| olist_order_payments_dataset.csv | paiements |
| olist_order_reviews_dataset.csv | avis (texte en portugais) |
| olist_orders_dataset.csv | commandes et dates de livraison |
| olist_products_dataset.csv | produits (poids, dimensions) |
| olist_sellers_dataset.csv | vendeurs |
| product_category_name_translation.csv | traduction des catégories PT → EN |
