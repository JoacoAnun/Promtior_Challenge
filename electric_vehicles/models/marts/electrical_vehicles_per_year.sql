{{ config(materialized='view')}}
-- How many electric vehicles are registered per year
SELECT 
	model_year,
	COUNT(*) AS vechicles_count
FROM {{ source('silver', 'electrical_vehicles_silver')}}
GROUP BY model_year
ORDER BY model_year