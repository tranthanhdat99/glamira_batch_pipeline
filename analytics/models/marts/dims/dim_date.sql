{{ config(materialized='table') }}

select
  time_key,
  full_date,
  hour,
  day_of_week,
  is_week_day,
  week_of_year,
  month,
  quarter,
  year
from {{ ref('stg_dim_dates') }};