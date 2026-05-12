{{ config(materialized='table')}}

/*
Columns are renamed to be more friendly to users. 
*/

SELECT 
    "VIN (1-10)" AS vin_1_10,
    "County" AS county,
    "City" AS city,
    "State" AS state,
    "Postal Code" AS postal_code,
    "Model Year" AS model_year,
    "Make" AS make,
    "Model" AS model,
    "Electric Vehicle Type" AS electric_vehicle_type,
    /*
    Convert strings to boolean. Easy to analyze if car is CAFV eligible.
    True - eligible,
    False - not eligible,
    NULL - unknown
    */
    CASE 
        WHEN "Clean Alternative Fuel Vehicle (CAFV) Eligibility" = 'Clean Alternative Fuel Vehicle Eligible' THEN True
        WHEN "Clean Alternative Fuel Vehicle (CAFV) Eligibility" = 'Not eligible due to low battery range' THEN False
        ELSE NULL
    END AS is_cafv_eligibility,
    "Electric Range" AS electric_range,
    "Legislative District" AS legislative_district,
    "DOL Vehicle ID" AS dol_vehicle_id,
    -- Convert POINT into separate coordinates, check right format, otherwise null the value.
    CASE 
        WHEN "Vehicle Location" LIKE 'POINT %' 
        	then SPLIT_PART(
                TRIM(REPLACE(REPLACE("Vehicle Location", 'POINT (', ''), ')', '')), 
                ' ', 1
            )::DECIMAL
        else null
    end as latitude,
    CASE 
        WHEN "Vehicle Location" LIKE 'POINT %' 
        	then SPLIT_PART(
                TRIM(REPLACE(REPLACE("Vehicle Location", 'POINT (', ''), ')', '')), 
                ' ', 2
            )::DECIMAL
        else null
    end as longitude,
    "Electric Utility" AS electric_utility,
    "2020 Census Tract" AS census_tract_2020
FROM {{ source('bronze', 'electrical_vehicles_bronze') }}