{{ config(materialized='table') }}

select
  store_key,
  store_name
from {{ ref('stg_dim_stores') }};