{{
    config(
        materialized='table'
    )
}}

SELECT
    pickup_location_id,
    distance_category,

    COUNT(*) AS trip_count,
    COUNT(DISTINCT dropoff_location_id) AS distinct_dropoff_zones,

    SUM(trip_distance) AS total_distance,
    AVG(trip_distance) AS avg_trip_distance,

    SUM(total_amount) AS total_revenue,
    AVG(total_amount) AS avg_trip_amount,

    AVG(trip_duration_minutes) AS avg_trip_duration_minutes,
    AVG(speed_kmh) AS avg_speed_kmh,
    AVG(tip_rate) AS avg_tip_rate,

    SUM(passenger_count) AS total_passengers

FROM {{ ref('int_clean_trips') }}

GROUP BY
    pickup_location_id,
    distance_category

ORDER BY
    pickup_location_id,
    distance_category