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
    TIME_PERIOD,
    SUM(TRIP_COUNT) AS TOTAL_TRIPS,
    ROUND(SUM(TOTAL_REVENUE), 2) AS TOTAL_REVENUE,
    ROUND(
        SUM(TOTAL_REVENUE) / NULLIF(SUM(TRIP_COUNT), 0),
        2
    ) AS REVENUE_PER_TRIP,
    ROUND(
        SUM(TOTAL_DISTANCE) / NULLIF(SUM(TRIP_COUNT), 0),
        2
    ) AS AVG_DISTANCE_KM
FROM NYC_TAXI.FINAL.HOURLY_PATTERNS
GROUP BY TIME_PERIOD
ORDER BY TOTAL_TRIPS DESC;
"""

try:
    with conn.cursor() as cur:
        cur.execute(query)

        columns = [col[0] for col in cur.description]

        print("\n=== ACTIVITE PAR PERIODE DE LA JOURNEE ===\n")
        print(" | ".join(columns))
        print("-" * 110)

        for row in cur.fetchall():
            print(" | ".join(str(value) for value in row))

finally:
    conn.close()