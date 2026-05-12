{{ config(materialized='view')}}

WITH registered_per_year_per_county AS (
    /*
    First obtain the number of electrical vehicles registered year and county
    */
    SELECT 
        model_year,
        county,
        COUNT(*) AS registered_vehicles
    FROM {{ ref('electrical_vehicles_silver')}}
    GROUP BY model_year, county
)
SELECT
    county,
    model_year,
    registered_vehicles,
    /*
    Previous year registration for better comparison
    */
    LAG(registered_vehicles, 1) OVER (
        PARTITION BY county 
        ORDER BY model_year
    ) AS registered_vehicles_previous_year,
    /*
    Calculate the percentage using window functions to compare current year vs previous year
    */
    ROUND((
        registered_vehicles - LAG(registered_vehicles, 1) OVER (
            PARTITION BY county ORDER BY model_year
        )
    ) * 100.0
        / LAG(registered_vehicles, 1) OVER (
            PARTITION BY county ORDER BY model_year
        ), 2
    ) AS yoy_change_prct
FROM registered_per_year_per_county
ORDER BY county, model_year