WITH invalid_measures AS (

    SELECT
        'daily_trips' AS model_name,
        pickup_date::VARCHAR AS grain_key
    FROM {{ ref('daily_trips') }}
    WHERE
        trip_count < 0
        OR total_distance < 0
        OR avg_trip_distance < 0
        OR total_revenue < 0
        OR avg_trip_amount < 0
        OR avg_trip_duration_minutes < 0
        OR total_passengers < 0

    UNION ALL

    SELECT
        'hourly_patterns' AS model_name,
        pickup_hour::VARCHAR AS grain_key
    FROM {{ ref('hourly_patterns') }}
    WHERE
        trip_count < 0
        OR total_distance < 0
        OR avg_trip_distance < 0
        OR total_revenue < 0
        OR avg_trip_amount < 0
        OR avg_trip_duration_minutes < 0
        OR total_passengers < 0

    UNION ALL

    SELECT
        'zone_analysis' AS model_name,
        pickup_location_id::VARCHAR AS grain_key
    FROM {{ ref('zone_analysis') }}
    WHERE
        trip_count < 0
        OR distinct_dropoff_zones < 0
        OR total_distance < 0
        OR avg_trip_distance < 0
        OR total_revenue < 0
        OR avg_trip_amount < 0
        OR avg_trip_duration_minutes < 0
        OR total_passengers < 0
)

SELECT *
FROM invalid_measures