{{ config(materialized='view') }}

-- 1) Explode cart_products for 'checkout_success' events
WITH exploded AS (
  SELECT
    SAFE_CAST(time_stamp AS INT64)                 AS ts_int,
    ip,
    store_id,
    order_id,
    product.product_id                             AS product_id,
    SAFE_CAST(product.amount AS INT64)             AS order_quantity,
    TRIM(product.price)                            AS raw_price,
    product.currency                               AS currency,
    (SELECT opt.value_label
       FROM UNNEST(product.option) AS opt
      WHERE opt.option_label = 'alloy'
      LIMIT 1)                                     AS alloy_name,
    (SELECT opt.value_label
       FROM UNNEST(product.option) AS opt
      WHERE opt.option_label = 'diamond'
      LIMIT 1)                                     AS stone_name
  FROM {{ source('glamira_raw', 'summary_raw') }},
       UNNEST(cart_products) AS product
  WHERE collection = 'checkout_success'
),

-- 2) Clean numeric price, derive date_key + hour
clean AS (
  SELECT
    ts_int,
    ip,
    SAFE_CAST(store_id AS INT64)                   AS store_id,
    TRY_CAST(order_id AS INT64)                    AS order_key,
    TRY_CAST(product_id AS INT64)                  AS product_key,
    order_quantity,
    currency,
    alloy_name,
    stone_name,
    CAST(
      REGEXP_REPLACE(
        CASE
          WHEN SUBSTR(raw_price, LENGTH(raw_price)-2, 1) = ',' AND raw_price LIKE '%.%' THEN
            REPLACE(REPLACE(raw_price, '.', ''), ',', '.')
          WHEN SUBSTR(raw_price, LENGTH(raw_price)-2, 1) = '.' AND raw_price LIKE '%,%' THEN
            REPLACE(REPLACE(raw_price, ',', ''), '.', ',')
          ELSE COALESCE(raw_price, '0')
        END,
        r'[^0-9\.]', ''
      ) AS FLOAT64
    )                                             AS unit_price,
    CAST(FORMAT_DATE('%Y%m%d', TIMESTAMP_SECONDS(ts_int)) AS INT64) AS date_key,
    EXTRACT(HOUR FROM TIMESTAMP_SECONDS(ts_int))               AS hour
  FROM exploded
),

-- 3) Convert to USD using stg_exchange_rates
enriched AS (
  SELECT
    c.*,
    er.exchange_rate_to_usd,
    c.unit_price * er.exchange_rate_to_usd         AS unit_price_usd,
    c.order_quantity * c.unit_price * er.exchange_rate_to_usd AS line_total_usd
  FROM clean AS c
  LEFT JOIN {{ ref('stg_exchange_rates') }} AS er
    ON c.currency = er.currency_symbol
),

-- 4) Final staging output
final AS (
  SELECT
    TRY_CAST(order_key AS INT64)                                 AS order_key,
    CAST(
      CONCAT(
        CAST(date_key AS STRING),
        LPAD(CAST(hour AS STRING), 2, '0')
      ) AS INT64
    )                                                            AS order_time_key,
    store_id                                                     AS store_key,
    product_key                                                  AS product_key,
    alloy_name                                                   AS alloy_name,
    stone_name                                                   AS stone_name,
    ip                                                           AS location_ip,
    order_quantity                                               AS order_quantity,
    unit_price_usd                                               AS unit_price,
    line_total_usd                                               AS line_total
  FROM enriched
)

SELECT * FROM final;
