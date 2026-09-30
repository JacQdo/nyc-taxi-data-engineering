from pathlib import Path
import sys
import urllib.request


# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"

# Racine du projet :
# ingestion/download_tlc_data.py
#        ↑ parent = ingestion
#        ↑ parent = projet
PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DIR = PROJECT_ROOT / "data" / "raw" / "yellow_taxi"


# ============================================================
# PARAMETRE ANNEE
# ============================================================

if len(sys.argv) != 2:
    print("Usage : python .\\ingestion\\download_tlc_data.py <année>")
    print("Exemple : python .\\ingestion\\download_tlc_data.py 2024")
    sys.exit(1)

YEAR = sys.argv[1]

if not YEAR.isdigit() or len(YEAR) != 4:
    print(f"[ERREUR] Année invalide : {YEAR}")
    print("Exemple : 2024")
    sys.exit(1)


# ============================================================
# DOSSIER DE DESTINATION
# ============================================================

OUTPUT_DIR = RAW_DIR / YEAR
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"=== TLC YELLOW TAXI {YEAR} ===")
print(f"[DESTINATION] {OUTPUT_DIR}")
print()


# ============================================================
# TELECHARGEMENT DES 12 MOIS
# ============================================================

for month in range(1, 13):

    filename = f"yellow_tripdata_{YEAR}-{month:02d}.parquet"

    url = f"{BASE_URL}/{filename}"
    output_file = OUTPUT_DIR / filename

    # Ne pas télécharger si le fichier existe déjà
    if output_file.exists():
        print(f"[DEJA PRESENT] {filename}")
        continue

    print(f"[TELECHARGEMENT] {filename}")

    try:
        urllib.request.urlretrieve(url, output_file)
        print(f"[OK] {output_file}")

    except Exception as e:
        print(f"[ERREUR] {filename}")
        print(f"         {e}")

        # Supprime un fichier partiellement téléchargé
        if output_file.exists():
            output_file.unlink()


print()
print(f"=== TELECHARGEMENT {YEAR} TERMINE ===")