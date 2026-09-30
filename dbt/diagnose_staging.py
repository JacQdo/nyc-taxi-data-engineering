import os
from pathlib import Path
import snowflake.connector

queries = {
"01 - VOLUME ET PERIODE": """SELECT COUNT(*) AS nb_lignes, MIN(pickup_datetime) AS min_pickup, MAX(pickup_datetime) AS max_pickup, COUNT_IF(pickup_datetime < '2022-01-01' OR pickup_datetime >= '2025-01-01') AS dates_hors_periode FROM NYC_TAXI.STAGING.STG_YELLOW_TAXI;""",
"02 - ANOMALIES DATES": """SELECT COUNT_IF(pickup_datetime < '2022-01-01') AS pickup_avant_2022, COUNT_IF(pickup_datetime >= '2025-01-01') AS pickup_depuis_2025, COUNT_IF(dropoff_datetime < '2022-01-01') AS dropoff_avant_2022, COUNT_IF(dropoff_datetime >= '2025-01-01') AS dropoff_depuis_2025, COUNT_IF(dropoff_datetime < pickup_datetime) AS dropoff_avant_pickup, COUNT_IF(pickup_datetime IS NULL) AS pickup_null, COUNT_IF(dropoff_datetime IS NULL) AS dropoff_null FROM NYC_TAXI.STAGING.STG_YELLOW_TAXI;""",
"03 - PASSAGERS": """SELECT COUNT_IF(passenger_count IS NULL) AS passenger_null, COUNT_IF(passenger_count <= 0) AS passenger_zero_ou_negatif, COUNT_IF(passenger_count > 9) AS passenger_superieur_9, MIN(passenger_count) AS min_passengers, MAX(passenger_count) AS max_passengers FROM NYC_TAXI.STAGING.STG_YELLOW_TAXI;""",
"04 - DISTANCES": """SELECT COUNT_IF(trip_distance IS NULL) AS distance_null, COUNT_IF(trip_distance < 0) AS distance_negative, COUNT_IF(trip_distance = 0) AS distance_zero, COUNT_IF(trip_distance > 200) AS distance_superieure_200, MIN(trip_distance) AS min_distance, MAX(trip_distance) AS max_distance FROM NYC_TAXI.STAGING.STG_YELLOW_TAXI;""",
"05 - MONTANTS": """SELECT COUNT_IF(total_amount IS NULL) AS total_null, COUNT_IF(total_amount < 0) AS total_negative, COUNT_IF(fare_amount < 0) AS fare_negative, COUNT_IF(tip_amount < 0) AS tip_negative, COUNT_IF(tolls_amount < 0) AS tolls_negative, MIN(total_amount) AS min_total, MAX(total_amount) AS max_total FROM NYC_TAXI.STAGING.STG_YELLOW_TAXI;""",
"06 - DUREE": """SELECT COUNT_IF(trip_duration_minutes IS NULL) AS duree_null, COUNT_IF(trip_duration_minutes < 0) AS duree_negative, COUNT_IF(trip_duration_minutes = 0) AS duree_zero, COUNT_IF(trip_duration_minutes > 1440) AS duree_superieure_24h, MIN(trip_duration_minutes) AS min_duree, MAX(trip_duration_minutes) AS max_duree FROM NYC_TAXI.STAGING.STG_YELLOW_TAXI;""",
"07 - LOCATIONS": """SELECT COUNT_IF(pickup_location_id IS NULL) AS pickup_location_null, COUNT_IF(dropoff_location_id IS NULL) AS dropoff_location_null, COUNT_IF(pickup_location_id <= 0) AS pickup_location_invalide, COUNT_IF(dropoff_location_id <= 0) AS dropoff_location_invalide, MIN(pickup_location_id) AS min_pickup_location, MAX(pickup_location_id) AS max_pickup_location, MIN(dropoff_location_id) AS min_dropoff_location, MAX(dropoff_location_id) AS max_dropoff_location FROM NYC_TAXI.STAGING.STG_YELLOW_TAXI;""",
"08 - DOUBLONS POTENTIELS": """SELECT vendor_id, pickup_datetime, dropoff_datetime, pickup_location_id, dropoff_location_id, trip_distance, total_amount, COUNT(*) AS nb FROM NYC_TAXI.STAGING.STG_YELLOW_TAXI GROUP BY vendor_id, pickup_datetime, dropoff_datetime, pickup_location_id, dropoff_location_id, trip_distance, total_amount HAVING COUNT(*) > 1 ORDER BY nb DESC LIMIT 20;"""
}

conn = snowflake.connector.connect(
    account=os.environ["SNOWFLAKE_ACCOUNT"],
    user=os.environ["SNOWFLAKE_USER"],
    password=os.environ["SNOWFLAKE_PASSWORD"],
    role="ACCOUNTADMIN",
    warehouse="NYC_TAXI_WH",
    database="NYC_TAXI",
    schema="STAGING"
)

output = Path("..") / "data" / "profiling" / "staging_diagnostic.txt"

with conn.cursor() as cur, output.open("w", encoding="utf-8") as f:
    for title, sql in queries.items():
        f.write("=" * 80 + "\n")
        f.write(title + "\n")
        f.write("=" * 80 + "\n")
        cur.execute(sql)
        columns = [d[0] for d in cur.description]
        f.write(" | ".join(columns) + "\n")
        f.write("-" * 80 + "\n")
        for row in cur.fetchall():
            f.write(" | ".join("" if v is None else str(v) for v in row) + "\n")
        f.write("\n")

conn.close()
print(f"Diagnostic terminé : {output.resolve()}")
