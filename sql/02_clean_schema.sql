CREATE SCHEMA IF NOT EXISTS clean;


DROP TABLE IF EXISTS clean.customers CASCADE;
CREATE TABLE clean.customers AS
SELECT
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state
FROM raw.customers;

ALTER TABLE clean.customers ADD PRIMARY KEY (customer_id);


DROP TABLE IF EXISTS clean.sellers CASCADE;
CREATE TABLE clean.sellers AS
SELECT
    seller_id,
    seller_zip_code_prefix,
    seller_city,
    seller_state
FROM raw.sellers;

ALTER TABLE clean.sellers ADD PRIMARY KEY (seller_id);


DROP TABLE IF EXISTS clean.product_category_name_translation CASCADE;
CREATE TABLE clean.product_category_name_translation AS
SELECT
    product_category_name,
    product_category_name_english
FROM raw.product_category_name_translation;

ALTER TABLE clean.product_category_name_translation ADD PRIMARY KEY (product_category_name);


DROP TABLE IF EXISTS clean.products CASCADE;
CREATE TABLE clean.products AS
SELECT
    product_id,
    product_category_name,
    product_name_length::INTEGER         AS product_name_length,
    product_description_length::INTEGER  AS product_description_length,
    product_photos_qty::INTEGER          AS product_photos_qty,
    product_weight_g::INTEGER            AS product_weight_g,
    product_length_cm::INTEGER           AS product_length_cm,
    product_height_cm::INTEGER           AS product_height_cm,
    product_width_cm::INTEGER            AS product_width_cm
FROM raw.products;

ALTER TABLE clean.products ADD PRIMARY KEY (product_id);


DROP TABLE IF EXISTS clean.orders CASCADE;
CREATE TABLE clean.orders AS
SELECT
    order_id,
    customer_id,
    order_status,
    order_purchase_timestamp::TIMESTAMP       AS order_purchase_timestamp,
    order_approved_at::TIMESTAMP              AS order_approved_at,
    order_delivered_carrier_date::TIMESTAMP   AS order_delivered_carrier_date,
    order_delivered_customer_date::TIMESTAMP  AS order_delivered_customer_date,
    order_estimated_delivery_date::TIMESTAMP  AS order_estimated_delivery_date
FROM raw.orders;

ALTER TABLE clean.orders ADD PRIMARY KEY (order_id);


DROP TABLE IF EXISTS clean.order_items CASCADE;
CREATE TABLE clean.order_items AS
SELECT
    order_id,
    order_item_id::INTEGER           AS order_item_id,
    product_id,
    seller_id,
    shipping_limit_date::TIMESTAMP   AS shipping_limit_date,
    price::NUMERIC                   AS price,
    freight_value::NUMERIC           AS freight_value
FROM raw.order_items;

ALTER TABLE clean.order_items ADD PRIMARY KEY (order_id, order_item_id);


DROP TABLE IF EXISTS clean.order_payments CASCADE;
CREATE TABLE clean.order_payments AS
SELECT
    order_id,
    payment_sequential::INTEGER    AS payment_sequential,
    payment_type,
    payment_installments::INTEGER  AS payment_installments,
    payment_value::NUMERIC         AS payment_value
FROM raw.order_payments;

ALTER TABLE clean.order_payments ADD PRIMARY KEY (order_id, payment_sequential);



DROP TABLE IF EXISTS clean.order_reviews CASCADE;
CREATE TABLE clean.order_reviews AS
SELECT DISTINCT ON (review_id, order_id)
    review_id,
    order_id,
    review_score::INTEGER                AS review_score,
    review_comment_title,
    review_comment_message,
    review_creation_date::TIMESTAMP      AS review_creation_date,
    review_answer_timestamp::TIMESTAMP   AS review_answer_timestamp
FROM raw.order_reviews
ORDER BY review_id, order_id;

ALTER TABLE clean.order_reviews ADD PRIMARY KEY (review_id, order_id);



DROP TABLE IF EXISTS clean.geolocation CASCADE;
CREATE TABLE clean.geolocation AS
SELECT
    geolocation_zip_code_prefix,
    AVG(geolocation_lat::NUMERIC)  AS geolocation_lat,
    AVG(geolocation_lng::NUMERIC)  AS geolocation_lng,
    MIN(geolocation_city)          AS geolocation_city,
    MIN(geolocation_state)         AS geolocation_state
FROM raw.geolocation
GROUP BY geolocation_zip_code_prefix;

ALTER TABLE clean.geolocation ADD PRIMARY KEY (geolocation_zip_code_prefix);


ALTER TABLE clean.orders
    ADD FOREIGN KEY (customer_id) REFERENCES clean.customers (customer_id);

ALTER TABLE clean.order_items
    ADD FOREIGN KEY (order_id) REFERENCES clean.orders (order_id);
ALTER TABLE clean.order_items
    ADD FOREIGN KEY (product_id) REFERENCES clean.products (product_id);
ALTER TABLE clean.order_items
    ADD FOREIGN KEY (seller_id) REFERENCES clean.sellers (seller_id);

ALTER TABLE clean.order_payments
    ADD FOREIGN KEY (order_id) REFERENCES clean.orders (order_id);

ALTER TABLE clean.order_reviews
    ADD FOREIGN KEY (order_id) REFERENCES clean.orders (order_id);


