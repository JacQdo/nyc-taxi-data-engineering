from pathlib import Path
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DIR = PROJECT_ROOT / "data" / "raw" / "yellow_taxi"
REPORT_DIR = PROJECT_ROOT / "data" / "profiling"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

YEARS = [2023, 2024]


# Colonnes utilisées pour le profilage.
# Certaines colonnes peuvent être absentes selon l'année.
PROFILE_COLUMNS = [
    "VendorID",
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
    "passenger_count",
    "trip_distance",
    "RatecodeID",
    "store_and_fwd_flag",
    "PULocationID",
    "DOLocationID",
    "payment_type",
    "fare_amount",
    "extra",
    "mta_tax",
    "tip_amount",
    "tolls_amount",
    "improvement_surcharge",
    "total_amount",
    "congestion_surcharge",
    "Airport_fee",
]


# ============================================================
# PROFILAGE D'UNE ANNEE
# ============================================================

def profile_year(year):

    year_dir = RAW_DIR / str(year)
    files = sorted(year_dir.glob("yellow_tripdata_*.parquet"))

    if not files:
        print(f"[ERREUR] Aucun fichier trouvé pour {year}")
        return

    print()
    print("=" * 70)
    print(f"PROFILAGE {year}")
    print("=" * 70)
    print(f"Fichiers trouvés : {len(files)}")

    total_rows = 0
    missing_rows = 0
    negative_amount = 0
    zero_distance = 0
    distance_over_1000 = 0
    invalid_duration = 0
    speed_over_100 = 0

    missing_by_column = {
        column: 0
        for column in PROFILE_COLUMNS
    }

    min_distance = None
    max_distance = None
    sum_distance = 0.0
    distance_count = 0

    min_amount = None
    max_amount = None
    sum_amount = 0.0
    amount_count = 0

    min_duration = None
    max_duration = None

    monthly_results = []

    # ========================================================
    # LECTURE MOIS PAR MOIS
    # ========================================================

    for file in files:

        print(f"\n[LECTURE] {file.name}")

        df = pd.read_parquet(file)

        rows = len(df)
        total_rows += rows

        # ----------------------------------------------------
        # Colonnes réellement présentes dans ce fichier
        # ----------------------------------------------------

        available_profile_columns = [
            column
            for column in PROFILE_COLUMNS
            if column in df.columns
        ]

        # ----------------------------------------------------
        # Valeurs manquantes
        # ----------------------------------------------------

        for column in PROFILE_COLUMNS:

            if column in df.columns:

                missing_by_column[column] += int(
                    df[column].isna().sum()
                )

        row_missing = (
            df[available_profile_columns]
            .isna()
            .any(axis=1)
        )

        missing_rows += int(row_missing.sum())

        # ----------------------------------------------------
        # Montants négatifs
        # ----------------------------------------------------

        negative_count = int(
            (df["total_amount"] < 0).sum()
        )

        negative_amount += negative_count

        # ----------------------------------------------------
        # Distances
        # ----------------------------------------------------

        zero_distance_count = int(
            (df["trip_distance"] == 0).sum()
        )

        distance_over_1000_count = int(
            (df["trip_distance"] > 1000).sum()
        )

        zero_distance += zero_distance_count
        distance_over_1000 += distance_over_1000_count

        # ----------------------------------------------------
        # Durée
        # ----------------------------------------------------

        duration_minutes = (
            df["tpep_dropoff_datetime"]
            - df["tpep_pickup_datetime"]
        ).dt.total_seconds() / 60

        invalid_duration_count = int(
            (duration_minutes <= 0).sum()
        )

        invalid_duration += invalid_duration_count

        # ----------------------------------------------------
        # Vitesse
        # ----------------------------------------------------

        valid_speed = (
            (duration_minutes > 0)
            & (df["trip_distance"] >= 0)
        )

        speed_mph = pd.Series(
            float("nan"),
            index=df.index
        )

        speed_mph.loc[valid_speed] = (
            df.loc[valid_speed, "trip_distance"]
            / (duration_minutes.loc[valid_speed] / 60)
        )

        speed_over_100_count = int(
            (speed_mph > 100).sum()
        )

        speed_over_100 += speed_over_100_count

        # ----------------------------------------------------
        # Statistiques distance
        # ----------------------------------------------------

        distance = df["trip_distance"].dropna()

        if len(distance) > 0:

            current_min = distance.min()
            current_max = distance.max()

            min_distance = (
                current_min
                if min_distance is None
                else min(min_distance, current_min)
            )

            max_distance = (
                current_max
                if max_distance is None
                else max(max_distance, current_max)
            )

            sum_distance += distance.sum()
            distance_count += len(distance)

        # ----------------------------------------------------
        # Statistiques montant
        # ----------------------------------------------------

        amount = df["total_amount"].dropna()

        if len(amount) > 0:

            current_min = amount.min()
            current_max = amount.max()

            min_amount = (
                current_min
                if min_amount is None
                else min(min_amount, current_min)
            )

            max_amount = (
                current_max
                if max_amount is None
                else max(max_amount, current_max)
            )

            sum_amount += amount.sum()
            amount_count += len(amount)

        # ----------------------------------------------------
        # Statistiques durée
        # ----------------------------------------------------

        duration_valid = duration_minutes.dropna()

        if len(duration_valid) > 0:

            current_min = duration_valid.min()
            current_max = duration_valid.max()

            min_duration = (
                current_min
                if min_duration is None
                else min(min_duration, current_min)
            )

            max_duration = (
                current_max
                if max_duration is None
                else max(max_duration, current_max)
            )

        # ----------------------------------------------------
        # Résultat mensuel
        # ----------------------------------------------------

        monthly_results.append({
            "year": year,
            "file": file.name,
            "rows": rows,
            "missing_rows": int(row_missing.sum()),
            "negative_total_amount": negative_count,
            "zero_distance": zero_distance_count,
            "distance_over_1000": distance_over_1000_count,
            "invalid_duration": invalid_duration_count,
            "speed_over_100_mph": speed_over_100_count,
        })

        # ----------------------------------------------------
        # Affichage mensuel
        # ----------------------------------------------------

        print(f"  lignes              : {rows:,}")
        print(
            f"  lignes avec manquant: "
            f"{int(row_missing.sum()):,}"
        )
        print(
            f"  montant négatif     : "
            f"{negative_count:,}"
        )
        print(
            f"  distance = 0        : "
            f"{zero_distance_count:,}"
        )
        print(
            f"  distance > 1000     : "
            f"{distance_over_1000_count:,}"
        )

    # ========================================================
    # RESULTATS ANNUELS
    # ========================================================

    missing_pct = (
        missing_rows / total_rows * 100
        if total_rows
        else 0
    )

    negative_pct = (
        negative_amount / total_rows * 100
        if total_rows
        else 0
    )

    zero_distance_pct = (
        zero_distance / total_rows * 100
        if total_rows
        else 0
    )

    distance_over_1000_pct = (
        distance_over_1000 / total_rows * 100
        if total_rows
        else 0
    )

    invalid_duration_pct = (
        invalid_duration / total_rows * 100
        if total_rows
        else 0
    )

    speed_over_100_pct = (
        speed_over_100 / total_rows * 100
        if total_rows
        else 0
    )

    # ========================================================
    # AFFICHAGE RESULTATS
    # ========================================================

    print()
    print("-" * 70)
    print(f"RESULTATS ANNUELS {year}")
    print("-" * 70)

    print(
        f"Total trajets              : "
        f"{total_rows:,}"
    )

    print(
        f"Lignes avec ≥ 1 manquant   : "
        f"{missing_rows:,} ({missing_pct:.2f} %)"
    )

    print(
        f"Total_amount négatif       : "
        f"{negative_amount:,} ({negative_pct:.2f} %)"
    )

    print(
        f"Distance = 0               : "
        f"{zero_distance:,} ({zero_distance_pct:.2f} %)"
    )

    print(
        f"Distance > 1000 miles      : "
        f"{distance_over_1000:,} "
        f"({distance_over_1000_pct:.4f} %)"
    )

    print(
        f"Durée <= 0                 : "
        f"{invalid_duration:,} "
        f"({invalid_duration_pct:.4f} %)"
    )

    print(
        f"Vitesse > 100 mph          : "
        f"{speed_over_100:,} "
        f"({speed_over_100_pct:.4f} %)"
    )

    # ========================================================
    # VALEURS MANQUANTES PAR COLONNE
    # ========================================================

    print()
    print("VALEURS MANQUANTES PAR COLONNE")

    for column, count in missing_by_column.items():

        percentage = (
            count / total_rows * 100
            if total_rows
            else 0
        )

        if count > 0:

            print(
                f"  {column:<25}"
                f"{count:>10,} "
                f"({percentage:>6.2f} %)"
            )

    # ========================================================
    # STATISTIQUES
    # ========================================================

    print()
    print("STATISTIQUES")

    average_distance = (
        sum_distance / distance_count
        if distance_count
        else 0
    )

    average_amount = (
        sum_amount / amount_count
        if amount_count
        else 0
    )

    print(
        f"Distance moyenne           : "
        f"{average_distance:.2f} miles"
    )

    print(
        f"Distance min               : "
        f"{min_distance}"
    )

    print(
        f"Distance max               : "
        f"{max_distance}"
    )

    print(
        f"Montant moyen              : "
        f"${average_amount:.2f}"
    )

    print(
        f"Montant min                : "
        f"${min_amount}"
    )

    print(
        f"Montant max                : "
        f"${max_amount}"
    )

    print(
        f"Durée min                  : "
        f"{min_duration:.2f} min"
    )

    print(
        f"Durée max                  : "
        f"{max_duration:.2f} min"
    )

    # ========================================================
    # EXPORT PROFIL ANNUEL
    # ========================================================

    annual_result = pd.DataFrame([{

        "year": year,

        "files": len(files),

        "total_trips": total_rows,

        "missing_rows": missing_rows,
        "missing_rows_pct": missing_pct,

        "negative_total_amount": negative_amount,
        "negative_total_amount_pct": negative_pct,

        "zero_distance": zero_distance,
        "zero_distance_pct": zero_distance_pct,

        "distance_over_1000": distance_over_1000,
        "distance_over_1000_pct": distance_over_1000_pct,

        "invalid_duration": invalid_duration,
        "invalid_duration_pct": invalid_duration_pct,

        "speed_over_100_mph": speed_over_100,
        "speed_over_100_mph_pct": speed_over_100_pct,

        "average_distance": average_distance,
        "min_distance": min_distance,
        "max_distance": max_distance,

        "average_total_amount": average_amount,
        "min_total_amount": min_amount,
        "max_total_amount": max_amount,

        "min_duration_minutes": min_duration,
        "max_duration_minutes": max_duration,

    }])

    annual_file = (
        REPORT_DIR / f"profile_{year}.csv"
    )

    missing_file = (
        REPORT_DIR / f"missing_{year}.csv"
    )

    monthly_file = (
        REPORT_DIR / f"monthly_profile_{year}.csv"
    )

    annual_result.to_csv(
        annual_file,
        index=False
    )

    # ========================================================
    # EXPORT MANQUANTS PAR COLONNE
    # ========================================================

    missing_result = pd.DataFrame(
        [
            {
                "year": year,
                "column": column,
                "missing_count": count,
                "missing_pct": (
                    count / total_rows * 100
                    if total_rows
                    else 0
                ),
            }

            for column, count
            in missing_by_column.items()
        ]
    )

    missing_result.to_csv(
        missing_file,
        index=False
    )

    # ========================================================
    # EXPORT MENSUEL
    # ========================================================

    pd.DataFrame(
        monthly_results
    ).to_csv(
        monthly_file,
        index=False
    )

    print()
    print(f"[OK] {annual_file}")
    print(f"[OK] {missing_file}")
    print(f"[OK] {monthly_file}")


# ============================================================
# EXECUTION
# ============================================================

for year in YEARS:
    profile_year(year)


print()
print("=" * 70)
print("PROFILAGE 2023 + 2024 TERMINE")
print("=" * 70)