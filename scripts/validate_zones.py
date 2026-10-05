import yaml
import snowflake.connector

with open("dbt/profiles.yml", "r", encoding="utf-8") as f:
    profiles = yaml.safe_load(f)

cfg = profiles["nyc_taxi"]["outputs"]["dev"]

conn = snowflake.connector.connect(
    account=cfg["account"],
    user=cfg["user"],
    password=cfg["password"],
    role=cfg["role"],
    database=cfg["database"],
    warehouse=cfg["warehouse"],
    schema=cfg["schema"],
)

query = """
SELECT
    PICKUP_LOCATION_ID,
    SUM(TRIP_COUNT) AS TOTAL_TRIPS,
    ROUND(SUM(TOTAL_REVENUE), 2) AS TOTAL_REVENUE,
    ROUND(
        SUM(TOTAL_REVENUE) / NULLIF(SUM(TRIP_COUNT), 0),
        2
    ) AS REVENUE_PER_TRIP,
    ROUND(SUM(TOTAL_DISTANCE), 2) AS TOTAL_DISTANCE_KM,
    ROUND(AVG(AVG_TRIP_DISTANCE), 2) AS AVG_DISTANCE_KM,
    ROUND(AVG(AVG_TRIP_DURATION_MINUTES), 2) AS AVG_DURATION_MINUTES,
    ROUND(AVG(AVG_SPEED_KMH), 2) AS AVG_SPEED_KMH,
    SUM(DISTINCT_DROPOFF_ZONES) AS SUM_DROPOFF_ZONES
FROM NYC_TAXI.FINAL.ZONE_ANALYSIS
GROUP BY PICKUP_LOCATION_ID
ORDER BY TOTAL_TRIPS DESC
LIMIT 10;
"""

try:
    with conn.cursor() as cur:
        cur.execute(query)

        columns = [col[0] for col in cur.description]

        print("\n=== TOP 10 ZONES DE DEPART PAR NOMBRE DE COURSES ===\n")
        print(" | ".join(columns))
        print("-" * 140)

        for row in cur.fetchall():
            print(" | ".join(str(value) for value in row))

finally:
    conn.close()