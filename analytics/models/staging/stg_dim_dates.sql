{{
  config(
    materialized='view'
  )
}}

-- Generate a full datetime dimension: all dates and hours
with date_series as (
  select
    date_add(date('2000-01-01'), interval day_offset day) as date_value
  from unnest(generate_array(0, 36524)) as day_offset
),

hour_series as (
select hour_of_day
  from unnest(generate_array(0, 23)) as hour_of_day
),

datetime_cte as (
  select
    -- Composite key: YYYYMMDDHH (e.g., 2025072215 for 3 PM on 2025-07-22)
    cast(concat(cast(format_date('%Y%m%d', date_value) as string),
                lpad(cast(hour_of_day as string), 2, '0')) as int64) as time_key,
    date_value as full_date,
    hour_of_day as hour,
    format_date('%A', date_value) as day_of_week,
    case
    when format_date('%A', date_value) in ('Saturday','Sunday') then false
    else true
    end as is_week_day,
    extract(isoweek from date_value) as week_of_year,
    extract(month from date_value) as month,
    extract(quarter from date_value) as quarter,
    extract(year from date_value) as year
  from date_series
  cross join hour_series
)

select * from datetime_cte;