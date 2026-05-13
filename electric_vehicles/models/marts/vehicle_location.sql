{{ config(materialized='view')}}

SELECT
    county,
    city,
    state,
    model_year,
    make,
    model,
    latitude,
    longitude,
    is_cafv_eligibility
FROM {{ ref('electrical_vehicles_silver')}}
WHERE latitude IS NOT NULL AND longitude IS NOT NULL
AND is_cafv_eligibility IS NOT NULL