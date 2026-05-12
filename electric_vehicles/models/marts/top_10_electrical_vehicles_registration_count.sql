{{ config(materialized='view')}}
-- How many electric vehicles are registered per year
SELECT 
	model_year,
	COUNT(*) AS vechicles_count
FROM {{ ref('electrical_vehicles_silver')}}
GROUP BY model_year
ORDER BY vechicles_count DESC
LIMIT 10