{{
  config(
    materialized='view'
  )
}}

with raw as (
  select *
  from {{ source('glamira_raw', 'summary_raw') }}
),
exploded as (
  select
    option.value_label as stone_name
  from raw
  cross join unnest(raw.cart_products) as cart_product
  cross join unnest(cart_product.option) as option
  where option.option_label = 'diamond'
),
staged as (
  select
    farm_fingerprint(trim(stone_name)) as stone_key,
    trim(stone_name) as stone_name
  from exploded
)

select distinct
  stone_key,
  stone_name
from staged

union all

select
  -1 as stone_key,
  'unknown' as stone_name;
