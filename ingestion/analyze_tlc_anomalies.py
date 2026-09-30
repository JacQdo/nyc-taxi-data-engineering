from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DIR = PROJECT_ROOT / "data" / "raw" / "yellow_taxi"
OUTPUT_DIR = PROJECT_ROOT / "data" / "profiling"

YEARS = [2023, 2024]

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# Colonnes utilisées pour l'analyse des valeurs manquantes.
# Certaines colonnes peuvent être absentes selon l'année.
MISSING_COLUMNS = [
    "passenger_count",
    "RatecodeID",
    "store_and_fwd_flag",
    "congestion_surcharge",
    "Airport_fee",
]


# ============================================================
# ANALYSE D'UN FICHIER
# ============================================================

def analyze_file(file_path, year, month):

    print(f"[ANALYSE] {file_path.name}")

    df = pd.read_parquet(file_path)

    total_rows = len(df)

    # --------------------------------------------------------
    # DUREE
    # --------------------------------------------------------

    df["duration_minutes"] = (
        df["tpep_dropoff_datetime"]
        - df["tpep_pickup_datetime"]
    ).dt.total_seconds() / 60

    # --------------------------------------------------------
    # VITESSE
    # --------------------------------------------------------

    df["speed_mph"] = (
        df["trip_distance"]
        / (df["duration_minutes"] / 60)
    )

    # --------------------------------------------------------
    # PERCENTILES
    # --------------------------------------------------------

    percentile_rows = []

    variables = {
        "trip_distance": "Distance (miles)",
        "total_amount": "Montant total ($)",
        "duration_minutes": "Durée (minutes)",
        "speed_mph": "Vitesse moyenne (mph)",
    }

    for column, label in variables.items():

        values = df[column].dropna()

        # Durées valides uniquement
        if column == "duration_minutes":
            values = values[values > 0]

        # Vitesses valides uniquement
        if column == "speed_mph":
            values = values[
                (values > 0)
                & (values != float("inf"))
                & (values != float("-inf"))
            ]

        if len(values) == 0:
            continue

        percentiles = values.quantile(
            [0.50, 0.90, 0.95, 0.99, 0.999]
        )

        percentile_rows.append(
            {
                "year": year,
                "month": month,
                "variable": label,
                "column": column,
                "count": len(values),
                "p50": percentiles[0.50],
                "p90": percentiles[0.90],
                "p95": percentiles[0.95],
                "p99": percentiles[0.99],
                "p99_9": percentiles[0.999],
            }
        )

    # --------------------------------------------------------
    # COLONNES MANQUANTES DISPONIBLES
    # --------------------------------------------------------

    available_missing_columns = [
        column
        for column in MISSING_COLUMNS
        if column in df.columns
    ]

    # --------------------------------------------------------
    # DEFINITIONS DES ANOMALIES
    # --------------------------------------------------------

    anomaly_definitions = {}

    # Valeurs manquantes
    if available_missing_columns:

        anomaly_definitions["missing_values"] = (
            df[available_missing_columns]
            .isna()
            .any(axis=1)
        )

    # Distance négative
    anomaly_definitions["negative_distance"] = (
        df["trip_distance"] < 0
    )

    # Distance nulle
    anomaly_definitions["zero_distance"] = (
        df["trip_distance"] == 0
    )

    # Distance > 1000 miles
    anomaly_definitions["distance_over_1000"] = (
        df["trip_distance"] > 1000
    )

    # Montant négatif
    anomaly_definitions["negative_total_amount"] = (
        df["total_amount"] < 0
    )

    # Montant nul
    anomaly_definitions["zero_total_amount"] = (
        df["total_amount"] == 0
    )

    # Durée <= 0
    anomaly_definitions["duration_less_or_equal_zero"] = (
        df["duration_minutes"] <= 0
    )

    # Durée > 24 heures
    anomaly_definitions["duration_over_24h"] = (
        df["duration_minutes"] > 24 * 60
    )

    # Vitesse > 100 mph
    anomaly_definitions["speed_over_100_mph"] = (
        df["speed_mph"] > 100
    )

    # Vitesse non exploitable
    anomaly_definitions["speed_invalid"] = (
        (df["speed_mph"] <= 0)
        | (df["speed_mph"] == float("inf"))
        | (df["speed_mph"] == float("-inf"))
    )

    # --------------------------------------------------------
    # RESULTATS ANOMALIES
    # --------------------------------------------------------

    anomaly_rows = []

    for anomaly_type, mask in anomaly_definitions.items():

        count = int(mask.sum())

        percentage = (
            count / total_rows * 100
            if total_rows > 0
            else 0
        )

        anomaly_rows.append(
            {
                "year": year,
                "month": month,
                "anomaly_type": anomaly_type,
                "count": count,
                "percentage": percentage,
            }
        )

    return percentile_rows, anomaly_rows


# ============================================================
# TRAITEMENT DES ANNEES
# ============================================================

for year in YEARS:

    year_dir = RAW_DIR / str(year)

    all_percentiles = []
    all_anomalies = []

    monthly_files = sorted(
        year_dir.glob(
            f"yellow_tripdata_{year}-*.parquet"
        )
    )

    print()
    print("=" * 60)
    print(f"ANALYSE QUALITE TLC {year}")
    print("=" * 60)

    for file_path in monthly_files:

        month = int(file_path.stem[-2:])

        percentiles, anomalies = analyze_file(
            file_path,
            year,
            month,
        )

        all_percentiles.extend(percentiles)
        all_anomalies.extend(anomalies)

    # ========================================================
    # EXPORT PERCENTILES
    # ========================================================

    percentiles_df = pd.DataFrame(
        all_percentiles
    )

    percentiles_file = (
        OUTPUT_DIR
        / f"percentiles_{year}.csv"
    )

    percentiles_df.to_csv(
        percentiles_file,
        index=False,
    )

    # ========================================================
    # EXPORT ANOMALIES MENSUELLES
    # ========================================================

    anomalies_df = pd.DataFrame(
        all_anomalies
    )

    monthly_anomalies_file = (
        OUTPUT_DIR
        / f"monthly_anomalies_{year}.csv"
    )

    anomalies_df.to_csv(
        monthly_anomalies_file,
        index=False,
    )

    # ========================================================
    # AGREGE ANNUEL
    # ========================================================

    annual_anomalies = (
        anomalies_df
        .groupby(
            "anomaly_type",
            as_index=False
        )
        .agg(
            count=("count", "sum")
        )
    )

    total_rows = 0

    for file_path in monthly_files:

        # Lecture uniquement du nombre de lignes
        df_month = pd.read_parquet(
            file_path,
            columns=["VendorID"]
        )

        total_rows += len(df_month)

    annual_anomalies["percentage"] = (
        annual_anomalies["count"]
        / total_rows
        * 100
    )

    annual_anomalies.insert(
        0,
        "year",
        year,
    )

    annual_anomalies_file = (
        OUTPUT_DIR
        / f"anomalies_{year}.csv"
    )

    annual_anomalies.to_csv(
        annual_anomalies_file,
        index=False,
    )

    # ========================================================
    # AFFICHAGE CONSOLE
    # ========================================================

    print()
    print(f"=== RESULTATS {year} ===")
    print()
    print("ANOMALIES :")

    for _, row in annual_anomalies.iterrows():

        print(
            f"  {row['anomaly_type']:<35} "
            f"{int(row['count']):>10,} "
            f"({row['percentage']:.3f} %)"
        )

    print()
    print(
        f"[OK] {percentiles_file}"
    )

    print(
        f"[OK] {monthly_anomalies_file}"
    )

    print(
        f"[OK] {annual_anomalies_file}"
    )


print()
print("=" * 60)
print("ANALYSE TERMINEE")
print("=" * 60)