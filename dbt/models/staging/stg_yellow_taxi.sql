{{
    config(
        materialized='view'
    )
}}

WITH source AS (

    SELECT
        VendorID,
        tpep_pickup_datetime,
        tpep_dropoff_datetime,
        passenger_count,
        trip_distance,
        RatecodeID,
        store_and_fwd_flag,
        PULocationID,
        DOLocationID,
        payment_type,
        fare_amount,
        extra,
        mta_tax,
        tip_amount,
        tolls_amount,
        improvement_surcharge,
        total_amount,
        congestion_surcharge,
        airport_fee

    FROM {{ source('raw', 'yellow_trips') }}

)

SELECT
    -- Identifiants
    VendorID AS vendor_id,
    PULocationID AS pickup_location_id,
    DOLocationID AS dropoff_location_id,
    RatecodeID AS rate_code_id,
    payment_type AS payment_type,

    -- Dates / heures
    tpep_pickup_datetime AS pickup_datetime,
    tpep_dropoff_datetime AS dropoff_datetime,

    -- Informations trajet
    passenger_count,
    trip_distance,
    store_and_fwd_flag,

    -- Montants
    fare_amount,
    extra,
    mta_tax,
    tip_amount,
    tolls_amount,
    improvement_surcharge,
    congestion_surcharge,
    airport_fee,
    total_amount,

    -- Colonnes dérivées
    CAST(tpep_pickup_datetime AS DATE) AS pickup_date,

    EXTRACT(
        YEAR FROM tpep_pickup_datetime
    ) AS pickup_year,

    EXTRACT(
        MONTH FROM tpep_pickup_datetime
    ) AS pickup_month,

    EXTRACT(
        DAY FROM tpep_pickup_datetime
    ) AS pickup_day,

    EXTRACT(
        HOUR FROM tpep_pickup_datetime
    ) AS pickup_hour,

    EXTRACT(
        DAYOFWEEK FROM tpep_pickup_datetime
    ) AS pickup_day_of_week,

    DATEDIFF(
        'minute',
        tpep_pickup_datetime,
        tpep_dropoff_datetime
    ) AS trip_duration_minutes

FROM source
