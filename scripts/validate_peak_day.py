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
    PICKUP_DATE,
    TRIP_COUNT,
    ROUND(TOTAL_REVENUE, 2) AS TOTAL_REVENUE,
    ROUND(
        TOTAL_REVENUE / NULLIF(TRIP_COUNT, 0),
        2
    ) AS REVENUE_PER_TRIP,
    ROUND(AVG_TRIP_DISTANCE, 2) AS AVG_DISTANCE_KM,
    ROUND(AVG_TRIP_DURATION_MINUTES, 2) AS AVG_DURATION_MINUTES,
    ROUND(AVG_SPEED_KMH, 2) AS AVG_SPEED_KMH,
    ROUND(AVG_TIP_RATE, 2) AS AVG_TIP_RATE
FROM NYC_TAXI.FINAL.DAILY_TRIPS
ORDER BY TRIP_COUNT DESC
LIMIT 10;
"""

try:
    with conn.cursor() as cur:
        cur.execute(query)

        columns = [col[0] for col in cur.description]

        print("\n=== TOP 10 JOURS PAR NOMBRE DE COURSES ===\n")
        print(" | ".join(columns))
        print("-" * 120)

        for row in cur.fetchall():
            print(" | ".join(str(value) for value in row))

finally:
    conn.close()