{{
  config(
    materialized='view'
  )
}}

-- Source: seed file `product_names.csv` loaded via dbt seeds
with raw_products as (
  select
    product_id,
    product_name
  from {{ ref('product_names') }}
)

select
  -- Convert product_id to numeric key if possible, else default to -1
  try_cast(product_id as int64) as product_key,
  product_name
from raw_products
where product_id is not null
  and product_name is not null

union all

select
  -1 as product_key,
  'unknown' as product_name;