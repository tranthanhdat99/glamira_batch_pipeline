{{ config(materialized='table') }}

select
  alloy_key,
  alloy_name,
  trim(
    array_to_string(
      regexp_extract_all(alloy_name, r'[A-Za-zÀ-ÖØ-öø-ÿ\s-]+'),
      ' '
    )
  ) as color_name,
  case
    when metal_key = 375 then '9k Gold'
    when metal_key = 585 then '14k Gold'
    when metal_key = 750 then '18k Gold'
    when metal_key = 925 then 'Silver'
    when metal_key = 950
         and regexp_contains(alloy_name, r'Platin') then 'Platinum'
    when metal_key = 950
         and regexp_contains(alloy_name, r'Palladium') then 'Palladium'
    else 'unknown'
  end as metal_name
from {{ ref('stg_dim_alloys') }};