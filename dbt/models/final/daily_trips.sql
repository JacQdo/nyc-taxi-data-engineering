{{
    config(
        materialized='table'
    )
}}

SELECT
    pickup_date,

    COUNT(*) AS trip_count,

    SUM(trip_distance) AS total_distance,

    AVG(trip_distance) AS avg_trip_distance,

    SUM(total_amount) AS total_revenue,

    AVG(total_amount) AS avg_trip_amount,

    AVG(trip_duration_minutes) AS avg_trip_duration_minutes,

    SUM(passenger_count) AS total_passengers

FROM {{ ref('int_clean_trips') }}

GROUP BY
    pickup_date

ORDER BY
    pickup_date