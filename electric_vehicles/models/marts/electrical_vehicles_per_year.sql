{{ config(materialized='view')}}
-- How many electric vehicles are registered per year
SELECT 
	model_year,
	COUNT(*)
FROM {{ ref('electrical_vehicles_silver')}}
GROUP BY model_year
ORDER BY model_year