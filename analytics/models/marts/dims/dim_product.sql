{{ config(materialized='table') }}

select
  product_key,
  product_name
from {{ ref('stg_dim_products') }};