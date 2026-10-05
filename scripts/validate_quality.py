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

queries = {
    "NEGATIVE_TRIPS": """
        SELECT COUNT(*)
        FROM NYC_TAXI.FINAL.DAILY_TRIPS
        WHERE TRIP_COUNT < 0
    """,

    "NEGATIVE_REVENUE": """
        SELECT COUNT(*)
        FROM NYC_TAXI.FINAL.DAILY_TRIPS
        WHERE TOTAL_REVENUE < 0
    """,

    "NEGATIVE_DISTANCE": """
        SELECT COUNT(*)
        FROM NYC_TAXI.FINAL.DAILY_TRIPS
        WHERE TOTAL_DISTANCE < 0
    """,

    "INVALID_AVG_DISTANCE": """
        SELECT COUNT(*)
        FROM NYC_TAXI.FINAL.DAILY_TRIPS
        WHERE AVG_TRIP_DISTANCE < 0
    """,

    "INVALID_AVG_DURATION": """
        SELECT COUNT(*)
        FROM NYC_TAXI.FINAL.DAILY_TRIPS
        WHERE AVG_TRIP_DURATION_MINUTES < 0
    """,

    "INVALID_AVG_SPEED": """
        SELECT COUNT(*)
        FROM NYC_TAXI.FINAL.DAILY_TRIPS
        WHERE AVG_SPEED_KMH < 0
    """,

    "INVALID_TIP_RATE": """
        SELECT COUNT(*)
        FROM NYC_TAXI.FINAL.DAILY_TRIPS
        WHERE AVG_TIP_RATE < 0
           OR AVG_TIP_RATE > 100
    """,

    "NULL_PICKUP_DATE": """
        SELECT COUNT(*)
        FROM NYC_TAXI.FINAL.DAILY_TRIPS
        WHERE PICKUP_DATE IS NULL
    """,

    "NULL_TRIP_COUNT": """
        SELECT COUNT(*)
        FROM NYC_TAXI.FINAL.DAILY_TRIPS
        WHERE TRIP_COUNT IS NULL
    """,

    "NULL_REVENUE": """
        SELECT COUNT(*)
        FROM NYC_TAXI.FINAL.DAILY_TRIPS
        WHERE TOTAL_REVENUE IS NULL
    """
}

try:
    with conn.cursor() as cur:

        print("\n=== CONTROLE QUALITE DES MARTS FINAL ===\n")

        all_passed = True

        for name, query in queries.items():
            cur.execute(query)
            result = cur.fetchone()[0]

            status = "PASS" if result == 0 else "FAIL"

            if result != 0:
                all_passed = False

            print(f"{status:<6} | {name:<25} | {result}")

        print("\n" + "-" * 60)

        if all_passed:
            print("RESULTAT GLOBAL : PASS")
        else:
            print("RESULTAT GLOBAL : FAIL")

finally:
    conn.close()