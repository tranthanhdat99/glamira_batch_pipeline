{{
  config(
    materialized='view'
  )
}}

with raw as (
  select *
  from {{ source('glamira_raw', 'summary_raw') }}
),

cleaned as (
  select
    -- Cast store_id to INT64 where possible; fallback to -1
    coalesce(safe_cast(store_id as int64), -1) as store_key,
    -- Normalize store name or mark 'unknown'
    case
      when store_id is null or trim(store_id) = '' then 'unknown'
      else concat('store-', trim(store_id))
    end as store_name
  from raw
)

select distinct
  store_key,
  store_name
from cleaned

-- Ensure 'unknown' fallback is present
union all
select
  -1 as store_key,
  'unknown' as store_name;