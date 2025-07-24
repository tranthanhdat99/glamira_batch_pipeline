{{
  config(
    materialized='view'
  )
}}

select
  currency_symbol,
  currency_code,
  currency_name,
  exchange_rate_to_usd
from {{ ref('exchange_rates') }}