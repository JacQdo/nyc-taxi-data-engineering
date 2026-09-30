{{
    config(
        materialized='table'
    )
}}

SELECT
    *
FROM {{ ref('stg_yellow_taxi') }}
WHERE
    pickup_datetime >= '2022-01-01'
    AND pickup_datetime < '2025-01-01'
    AND dropoff_datetime >= pickup_datetime
    AND (
        passenger_count IS NULL
        OR passenger_count > 0
    )
    AND trip_distance <= 200
    AND total_amount >= 0
    AND fare_amount >= 0
    AND tip_amount >= 0
    AND tolls_amount >= 0
    AND trip_duration_minutes >= 0
    AND trip_duration_minutes <= 1440