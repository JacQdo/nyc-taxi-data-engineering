{{
    config(
        materialized='table'
    )
}}

SELECT
    pickup_location_id,

    COUNT(*) AS trip_count,

    COUNT(DISTINCT dropoff_location_id) AS distinct_dropoff_zones,

    SUM(trip_distance) AS total_distance,

    AVG(trip_distance) AS avg_trip_distance,

    SUM(total_amount) AS total_revenue,

    AVG(total_amount) AS avg_trip_amount,

    AVG(trip_duration_minutes) AS avg_trip_duration_minutes,

    SUM(passenger_count) AS total_passengers

FROM {{ ref('int_clean_trips') }}

GROUP BY
    pickup_location_id

ORDER BY
    trip_count DESC