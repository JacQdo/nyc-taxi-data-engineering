import os
import snowflake.connector

sql = """
SELECT
    COUNT(*) AS lignes_initiales,

    COUNT_IF(
        pickup_datetime >= '2022-01-01'
        AND pickup_datetime < '2025-01-01'
        AND dropoff_datetime >= pickup_datetime
        AND (passenger_count IS NULL OR passenger_count > 0)
        AND trip_distance <= 200
        AND total_amount >= 0
        AND fare_amount >= 0
        AND tip_amount >= 0
        AND tolls_amount >= 0
        AND trip_duration_minutes >= 0
        AND trip_duration_minutes <= 1440
    ) AS lignes_conservees,

    COUNT_IF(
        NOT (
            pickup_datetime >= '2022-01-01'
            AND pickup_datetime < '2025-01-01'
            AND dropoff_datetime >= pickup_datetime
            AND (passenger_count IS NULL OR passenger_count > 0)
            AND trip_distance <= 200
            AND total_amount >= 0
            AND fare_amount >= 0
            AND tip_amount >= 0
            AND tolls_amount >= 0
            AND trip_duration_minutes >= 0
            AND trip_duration_minutes <= 1440
        )
    ) AS lignes_rejetees

FROM NYC_TAXI.STAGING.STG_YELLOW_TAXI;
"""

conn = snowflake.connector.connect(
    account=os.environ["SNOWFLAKE_ACCOUNT"],
    user=os.environ["SNOWFLAKE_USER"],
    password=os.environ["SNOWFLAKE_PASSWORD"],
    role="ACCOUNTADMIN",
    warehouse="NYC_TAXI_WH",
    database="NYC_TAXI",
    schema="STAGING"
)

with conn.cursor() as cur:
    cur.execute(sql)
    columns = [d[0] for d in cur.description]
    row = cur.fetchone()

    print()
    print("=" * 60)
    print("SIMULATION INT_CLEAN_TRIPS")
    print("=" * 60)
    for name, value in zip(columns, row):
        print(f"{name:<25} : {value:,}".replace(",", " "))
    print("=" * 60)

conn.close()
