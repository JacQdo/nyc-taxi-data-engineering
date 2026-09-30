import argparse
import os
from pathlib import Path

import snowflake.connector


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = PROJECT_ROOT / "data" / "raw" / "yellow_taxi"

DATABASE = "NYC_TAXI"
SCHEMA = "RAW"
WAREHOUSE = "NYC_TAXI_WH"
ROLE = "ACCOUNTADMIN"

STAGE = f"{DATABASE}.{SCHEMA}.YELLOW_TAXI_STAGE"
TABLE = f"{DATABASE}.{SCHEMA}.YELLOW_TRIPS"
FILE_FORMAT = f"{DATABASE}.{SCHEMA}.PARQUET_FORMAT"


# ============================================================
# CONNEXION SNOWFLAKE
# ============================================================

def get_connection():
    required = {
        "SNOWFLAKE_ACCOUNT": os.getenv("SNOWFLAKE_ACCOUNT"),
        "SNOWFLAKE_USER": os.getenv("SNOWFLAKE_USER"),
        "SNOWFLAKE_PASSWORD": os.getenv("SNOWFLAKE_PASSWORD"),
    }

    missing = [
        name
        for name, value in required.items()
        if not value
    ]

    if missing:
        raise RuntimeError(
            "Variables d'environnement manquantes : "
            + ", ".join(missing)
        )

    return snowflake.connector.connect(
        account=required["SNOWFLAKE_ACCOUNT"],
        user=required["SNOWFLAKE_USER"],
        password=required["SNOWFLAKE_PASSWORD"],
        role=ROLE,
        warehouse=WAREHOUSE,
        database=DATABASE,
        schema=SCHEMA,
    )


# ============================================================
# CREATION DES OBJETS RAW
# ============================================================

def create_raw_objects(conn):
    statements = [
        f"""
        CREATE SCHEMA IF NOT EXISTS {DATABASE}.{SCHEMA}
        """,

        f"""
        CREATE FILE FORMAT IF NOT EXISTS {FILE_FORMAT}
        TYPE = PARQUET
        USE_LOGICAL_TYPE = TRUE
        USE_VECTORIZED_SCANNER = TRUE
        BINARY_AS_TEXT = FALSE
        """,

        f"""
        CREATE STAGE IF NOT EXISTS {STAGE}
        FILE_FORMAT = {FILE_FORMAT}
        """,

        f"""
        CREATE TABLE IF NOT EXISTS {TABLE} (
            VendorID NUMBER,
            tpep_pickup_datetime TIMESTAMP_NTZ,
            tpep_dropoff_datetime TIMESTAMP_NTZ,
            passenger_count FLOAT,
            trip_distance FLOAT,
            RatecodeID FLOAT,
            store_and_fwd_flag VARCHAR,
            PULocationID NUMBER,
            DOLocationID NUMBER,
            payment_type NUMBER,
            fare_amount FLOAT,
            extra FLOAT,
            mta_tax FLOAT,
            tip_amount FLOAT,
            tolls_amount FLOAT,
            improvement_surcharge FLOAT,
            total_amount FLOAT,
            congestion_surcharge FLOAT,
            airport_fee FLOAT
        )
        """,
    ]

    with conn.cursor() as cur:
        for statement in statements:
            cur.execute(statement)


# ============================================================
# UPLOAD + COPY D'UN SEUL FICHIER
# ============================================================

def upload_and_copy(conn, parquet_file):
    stage_path = f"@{STAGE}"

    # Nom du fichier uniquement
    file_name = parquet_file.name

    with conn.cursor() as cur:

        print()
        print("----------------------------------------")
        print(f"Fichier : {file_name}")
        print("----------------------------------------")

        # ----------------------------------------------------
        # 1. UPLOAD DU FICHIER VERS LE STAGE
        # ----------------------------------------------------

        put_sql = f"""
        PUT 'file://{parquet_file.as_posix()}'
        {stage_path}
        AUTO_COMPRESS=FALSE
        PARALLEL=4
        """

        put_result = cur.execute(put_sql).fetchall()

        for row in put_result:
            print("PUT :", row)

        # ----------------------------------------------------
        # 2. COPY UNIQUEMENT DU FICHIER UPLOADÉ
        # ----------------------------------------------------

        copy_sql = f"""
        COPY INTO {TABLE}
        FROM (
            SELECT
                $1:VendorID::NUMBER,

                TO_TIMESTAMP_NTZ(
                    ($1:tpep_pickup_datetime::NUMBER) / 1000000
                ),

                TO_TIMESTAMP_NTZ(
                    ($1:tpep_dropoff_datetime::NUMBER) / 1000000
                ),

                $1:passenger_count::FLOAT,
                $1:trip_distance::FLOAT,
                $1:RatecodeID::FLOAT,
                $1:store_and_fwd_flag::VARCHAR,
                $1:PULocationID::NUMBER,
                $1:DOLocationID::NUMBER,
                $1:payment_type::NUMBER,
                $1:fare_amount::FLOAT,
                $1:extra::FLOAT,
                $1:mta_tax::FLOAT,
                $1:tip_amount::FLOAT,
                $1:tolls_amount::FLOAT,
                $1:improvement_surcharge::FLOAT,
                $1:total_amount::FLOAT,
                $1:congestion_surcharge::FLOAT,
                $1:airport_fee::FLOAT

            FROM {stage_path}
        )

        FILES = ('{file_name}')

        FILE_FORMAT = (
            FORMAT_NAME = '{FILE_FORMAT}'
        )

        ON_ERROR = ABORT_STATEMENT
        """

        copy_result = cur.execute(copy_sql).fetchall()

        for row in copy_result:
            print("COPY :", row)


# ============================================================
# RECHERCHE DES FICHIERS
# ============================================================

def get_files(year, month=None):

    year_dir = DATA_ROOT / str(year)

    if not year_dir.exists():
        raise FileNotFoundError(
            f"Dossier introuvable : {year_dir}"
        )

    files = sorted(
        year_dir.glob("*.parquet")
    )

    # --------------------------------------------------------
    # Filtre sur le mois demandé
    # --------------------------------------------------------

    if month is not None:

        prefix = (
            f"yellow_tripdata_{year}-{month:02d}.parquet"
        )

        files = [
            file
            for file in files
            if file.name == prefix
        ]

    if not files:

        raise FileNotFoundError(
            f"Aucun fichier Parquet trouvé pour {year}"
            + (
                f"-{month:02d}"
                if month
                else ""
            )
        )

    return files


# ============================================================
# PROGRAMME PRINCIPAL
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Ingestion Yellow Taxi Parquet "
            "vers Snowflake RAW"
        )
    )

    parser.add_argument(
        "--year",
        type=int,
        required=True,
        choices=[2022, 2023, 2024],
        help="Année à charger",
    )

    parser.add_argument(
        "--month",
        type=int,
        choices=range(1, 13),
        help=(
            "Mois à charger. "
            "Sans cette option : toute l'année."
        ),
    )

    args = parser.parse_args()

    # --------------------------------------------------------
    # Recherche des fichiers
    # --------------------------------------------------------

    files = get_files(
        args.year,
        args.month
    )

    # --------------------------------------------------------
    # Affichage
    # --------------------------------------------------------

    print()
    print("========================================")
    print("NYC TAXI - INGESTION SNOWFLAKE RAW")
    print("========================================")
    print(f"Année       : {args.year}")
    print(
        f"Mois        : "
        f"{args.month or 'tous'}"
    )
    print(f"Fichiers    : {len(files)}")
    print()

    # --------------------------------------------------------
    # Connexion Snowflake
    # --------------------------------------------------------

    conn = get_connection()

    try:

        # ----------------------------------------------------
        # Création des objets RAW
        # ----------------------------------------------------

        create_raw_objects(conn)

        print("Objets RAW Snowflake : OK")

        # ----------------------------------------------------
        # Chargement des fichiers
        # ----------------------------------------------------

        for parquet_file in files:

            upload_and_copy(
                conn,
                parquet_file
            )

        # ----------------------------------------------------
        # Fin
        # ----------------------------------------------------

        print()
        print("========================================")
        print("INGESTION TERMINEE")
        print("========================================")

    finally:

        conn.close()


# ============================================================
# POINT D'ENTRÉE
# ============================================================

if __name__ == "__main__":
    main()