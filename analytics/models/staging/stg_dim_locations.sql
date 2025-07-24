{{ config(materialized='view') }}

with raw_locations as (
  select
    ip,
    city,
    region,
    country_short,
    country_long
  from {{ source('glamira_raw','ip_locations_raw') }}
),

cleaned as (
  select
    ip,
    case when city is null or trim(city) in ('','-') then 'unknown' else trim(city) end            as city_name,
    case when region is null or trim(region) in ('','-') then 'unknown' else trim(region) end      as region_name,
    case when country_short is null or trim(country_short) in ('','-') then 'unknown' else trim(country_short) end as country_short_name,
    case when country_long is null or trim(country_long) in ('','-') then 'unknown' else trim(country_long) end   as country_long_name
  from raw_locations
),

staged_locations as (
  select distinct
    ip,
    farm_fingerprint(concat(city_name, region_name, country_short_name, country_long_name)) as location_key,
    city_name,
    region_name,
    country_short_name,
    country_long_name
  from cleaned
)

select * from staged_locations

union all

select
  null                as ip,
  -1                  as location_key,
  'unknown'           as city_name,
  'unknown'           as region_name,
  'unknown'           as country_short_name,
  'unknown'           as country_long_name;
