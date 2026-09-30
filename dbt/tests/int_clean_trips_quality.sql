SELECT *
FROM {{ ref('int_clean_trips') }}
WHERE
    pickup_datetime < '2022-01-01'
    OR pickup_datetime >= '2025-01-01'
    OR dropoff_datetime < pickup_datetime
    OR (
        passenger_count IS NOT NULL
        AND passenger_count <= 0
    )
    OR trip_distance > 200
    OR total_amount < 0
    OR fare_amount < 0
    OR tip_amount < 0
    OR tolls_amount < 0
    OR trip_duration_minutes < 0
    OR trip_duration_minutes > 1440