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
        option
    from raw,
         unnest(raw.cart_products) as cart_product,
         unnest(cart_product.option) as option
    where option.option_label = 'alloy'
),
alloy_values as (
    select
        trim(value_part) as alloy_name
    from exploded,
         unnest(split(option.value_label, '/')) as value_part
),
staged as (
    select
        farm_fingerprint(trim(alloy_name)) as alloy_key,
        trim(alloy_name) as alloy_name,
        trim(
          array_to_string(
            regexp_extract_all(alloy_name, r'[A-Za-zÀ-ÖØ-öø-ÿ\s-]+'),
            ' '
          )
        ) as color_name,
        coalesce(
          safe_cast(regexp_extract(alloy_name, r'(\d+)') as int64),
          -1
        ) as metal_key
    from alloy_values
)

select distinct
    alloy_key,
    alloy_name,
    color_name,
    case
      when metal_key = 375 then '9k Gold'
      when metal_key = 585 then '14k Gold'
      when metal_key = 750 then '18k Gold'
      when metal_key = 925 then 'Silver'
      when metal_key = 950 then 'Platinum'
      else 'unknown'
    end as metal_name
from staged

union all

select
    -1 as alloy_key,
    'unknown' as alloy_name,
    'unknown' as color_name,
    'unknown' as metal_name;
