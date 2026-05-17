{{ config(materialized='view')}}
-- How many electric vehicles are registered per year
SELECT 
	model,
	COUNT(*) AS vehicles_count
FROM {{ ref('electrical_vehicles_silver')}}
GROUP BY model
ORDER BY vehicles_count DESC
LIMIT 10