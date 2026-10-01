{{
    config(
        materialized='table'
    )
}}

WITH cleaned AS (

    SELECT
        *
    FROM {{ ref('stg_yellow_taxi') }}
    WHERE
        pickup_datetime >= '2022-01-01'
        AND pickup_datetime < '2025-01-01'

        -- Cohérence temporelle
        AND dropoff_datetime >= pickup_datetime

        -- Nombre de passagers :
        -- les valeurs NULL sont conservées car elles représentent
        -- une information manquante et non une valeur nécessairement invalide.
        AND (
            passenger_count IS NULL
            OR passenger_count > 0
        )

        -- Distance aberrante
        AND trip_distance <= 200

        -- Montants négatifs
        AND total_amount >= 0
        AND fare_amount >= 0
        AND tip_amount >= 0
        AND tolls_amount >= 0

        -- Durée cohérente
        AND trip_duration_minutes >= 0
        AND trip_duration_minutes <= 1440
)

SELECT
    *,

    -- ============================================================
    -- ENRICHISSEMENTS
    -- ============================================================

    -- Vitesse moyenne en km/h.
    -- Une vitesse supérieure à 120 km/h est considérée comme
    -- aberrante pour l'analyse d'un trajet de taxi urbain.
    CASE
        WHEN trip_duration_minutes > 0
             AND trip_distance / (trip_duration_minutes / 60.0) <= 120
        THEN trip_distance / (trip_duration_minutes / 60.0)
        ELSE NULL
    END AS speed_kmh,

    -- Taux de pourboire en pourcentage du montant de la course.
    -- Un taux supérieur à 100 % est considéré comme aberrant
    -- pour l'analyse et est donc conservé sous forme de NULL.
    CASE
        WHEN fare_amount > 0
             AND (tip_amount / fare_amount) * 100 <= 100
        THEN (tip_amount / fare_amount) * 100
        ELSE NULL
    END AS tip_rate,

    -- Catégorisation de la distance.
    CASE
        WHEN trip_distance < 2 THEN '0-2 km'
        WHEN trip_distance < 5 THEN '2-5 km'
        WHEN trip_distance < 10 THEN '5-10 km'
        ELSE '10+ km'
    END AS distance_category,

    -- Catégorisation de la période horaire.
    CASE
        WHEN pickup_hour BETWEEN 0 AND 5 THEN 'Nuit'
        WHEN pickup_hour BETWEEN 6 AND 11 THEN 'Matin'
        WHEN pickup_hour BETWEEN 12 AND 17 THEN 'Après-midi'
        ELSE 'Soirée'
    END AS time_period,

    -- Type de jour.
    CASE
        WHEN pickup_day_of_week IN (0, 6) THEN 'Weekend'
        ELSE 'Weekday'
    END AS day_type

FROM cleaned