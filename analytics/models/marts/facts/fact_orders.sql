{{ config(materialized='table') }}

with src as (
  select *
  from {{ ref('stg_fact_orders') }} 
),

dim_keys as (
  select
    src.order_key,
    src.order_time_key,
    src.store_key,
    src.product_key,
    a.alloy_key   as alloy_key,
    s.stone_key   as stone_key,
    l.location_key as location_key,
    src.order_quantity,
    src.unit_price,
    src.line_total
  from src
  left join {{ ref('dim_alloy') }}    as a on src.alloy_name  = a.alloy_name
  left join {{ ref('dim_stone') }}    as s on src.stone_name  = s.stone_name
  left join {{ ref('stg_dim_locations') }} as l on src.ip = l.ip
),

fact as (
  select
    -- composite PK: fingerprint of business keys
    farm_fingerprint(
       concat(
         cast(order_key        as string),
         cast(order_time_key   as string),
         cast(product_key      as string)
       )
    )                                     as order_line_key,
    order_key,
    order_time_key,
    store_key,
    product_key,
    alloy_key,
    stone_key,
    location_key,
    order_quantity,
    unit_price,
    line_total
  from dim_keys
)

select * from fact;
