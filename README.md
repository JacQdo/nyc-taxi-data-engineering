# NYC Taxi Data Engineering

Pipeline Data Engineering complet construit autour de données NYC Yellow Taxi 2022–2024.

Le projet met en œuvre une architecture **Python + Snowflake + dbt**, avec séparation des couches RAW, STAGING, INTERMEDIATE et FINAL, règles de qualité, enrichissements analytiques et tests automatisés.

## Objectifs

* Ingérer des données Parquet volumineuses dans Snowflake.
* Conserver une couche RAW exploitable.
* Standardiser et typer les données avec dbt.
* Identifier et filtrer les anomalies de qualité.
* Enrichir les trajets avec des indicateurs analytiques.
* Construire plusieurs modèles métiers dans la couche FINAL.
* Automatiser les contrôles de qualité avec les tests dbt.
* Produire une base exploitable pour du reporting et de la BI.

## Architecture

```text
Parquet 2022–2024
       │
       ▼
Python / ingestion
       │
       ▼
Snowflake Internal Stage
       │
       ▼
RAW.YELLOW_TRIPS
       │
       ▼
STAGING.STG_YELLOW_TAXI
       │
       ▼
INTERMEDIATE.INT_CLEAN_TRIPS
       │
       ├──────────────► FINAL.DAILY_TRIPS
       │
       ├──────────────► FINAL.HOURLY_PATTERNS
       │
       └──────────────► FINAL.ZONE_ANALYSIS
```

### Séparation des responsabilités

| Composant  | Responsabilité                    |
| ---------- | --------------------------------- |
| Python     | ingestion et chargement           |
| Snowflake  | stockage et exécution SQL         |
| dbt        | transformations, modèles et tests |
| DuckDB     | contrôles exploratoires locaux    |
| Git/GitHub | versionnement du code             |

## Données

Le projet exploite 36 fichiers Parquet correspondant aux années 2022, 2023 et 2024.

### Volume local

* 36 fichiers Parquet
* environ 1,81 Go compressés
* 119 136 044 lignes identifiées avec DuckDB

### Volume chargé dans Snowflake

* 100 319 438 lignes dans RAW
* 100 318 800 lignes appartenant à la période cible 2022–2024
* 638 lignes présentant une date de pickup hors période cible

La différence entre le volume local et le volume chargé dans Snowflake constitue un point de contrôle identifié dans le projet et n'est pas présentée comme une parité parfaite entre les deux environnements.

## Couche RAW

Les fichiers sont chargés dans Snowflake via un **Internal Stage**.

```text
Parquet
   ↓
PUT
   ↓
Internal Stage
   ↓
COPY INTO
   ↓
RAW.YELLOW_TRIPS
```

La couche RAW constitue la source des transformations dbt.

## STAGING

Le modèle :

```text
STAGING.STG_YELLOW_TAXI
```

standardise notamment les noms de colonnes et ajoute plusieurs attributs temporels :

* date de pickup ;
* année ;
* mois ;
* jour ;
* heure ;
* jour de la semaine ;
* durée du trajet.

## Nettoyage

Le modèle :

```text
INTERMEDIATE.INT_CLEAN_TRIPS
```

applique les principales règles de qualité :

* période 2022–2024 ;
* dropoff >= pickup ;
* nombre de passagers positif lorsqu'il est renseigné ;
* distance <= 200 km ;
* montants non négatifs ;
* durée comprise entre 0 et 1 440 minutes.

### Résultat du nettoyage

```text
Lignes initiales       100 319 438
Lignes conservées       97 643 478
Lignes rejetées          2 675 960

Taux de conservation       97,33 %
Taux de rejet                2,67 %
```

Les valeurs manquantes de `passenger_count` sont conservées et documentées plutôt que remplacées artificiellement.

## Enrichissements

`int_clean_trips` ajoute :

* `speed_kmh`
* `tip_rate`
* `distance_category`
* `time_period`
* `day_type`

### Catégories de distance

| Catégorie | Nombre de trajets |
| --------- | ----------------: |
| 0–2 km    |        52 727 033 |
| 2–5 km    |        27 998 031 |
| 5–10 km   |         8 755 384 |
| 10+ km    |         8 163 030 |

Des seuils analytiques sont également appliqués aux indicateurs dérivés :

* vitesse maximale analytique : 120 km/h ;
* taux de pourboire maximal analytique : 100 %.

## Modèles FINAL

### `daily_trips`

Grain : **un jour**

920 lignes.

Principaux indicateurs :

* nombre de trajets ;
* chiffre d'affaires ;
* distance ;
* durée ;
* vitesse ;
* taux de pourboire ;
* passagers.

### `hourly_patterns`

Grain : **heure × type de jour**

48 lignes.

Permet d'analyser les comportements selon :

* l'heure ;
* la période de la journée ;
* Weekday / Weekend ;
* le volume ;
* le chiffre d'affaires ;
* la vitesse ;
* le pourboire.

### `zone_analysis`

Grain : **zone de départ × catégorie de distance**

1 048 lignes.

Permet d'étudier :

* les zones de départ ;
* les distances ;
* les destinations distinctes ;
* le chiffre d'affaires ;
* la durée ;
* la vitesse ;
* le taux de pourboire.

## Tests dbt

Les trois modèles finaux disposent de tests de qualité.

Dernière exécution :

```text
22 tests
22 PASS
0 WARN
0 ERROR
```

Les tests comprennent notamment :

* `not_null`
* `unique`
* `unique_combination`
* contrôles de mesures finales.

Les grains analytiques sont contrôlés par des tests d'unicité composite :

```text
hourly_patterns
pickup_hour + day_type
```

```text
zone_analysis
pickup_location_id + distance_category
```

## Documentation dbt

La documentation et le catalogue peuvent être générés avec :

```powershell
.\.venv\Scripts\dbt.exe docs generate `
  --project-dir .\dbt `
  --profiles-dir "$HOME\.dbt"
```

## Installation

Créer l'environnement Python :

```powershell
python -m venv .venv
```

Activer l'environnement :

```powershell
.\.venv\Scripts\Activate.ps1
```

Installer les dépendances :

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Configuration Snowflake

Le mot de passe Snowflake n'est pas stocké dans Git.

Le profil dbt utilise une variable d'environnement :

```yaml
password: "{{ env_var('SNOWFLAKE_PASSWORD') }}"
```

Dans PowerShell :

```powershell
$env:SNOWFLAKE_PASSWORD = Read-Host "Mot de passe Snowflake"
```

## Commandes dbt principales

Vérifier la configuration :

```powershell
.\.venv\Scripts\dbt.exe debug `
  --project-dir .\dbt `
  --profiles-dir "$HOME\.dbt"
```

Lister les modèles :

```powershell
.\.venv\Scripts\dbt.exe ls `
  --project-dir .\dbt `
  --profiles-dir "$HOME\.dbt"
```

Construire les modèles :

```powershell
.\.venv\Scripts\dbt.exe run `
  --project-dir .\dbt `
  --profiles-dir "$HOME\.dbt"
```

Tester les modèles finaux :

```powershell
.\.venv\Scripts\dbt.exe test `
  --select daily_trips hourly_patterns zone_analysis `
  --project-dir .\dbt `
  --profiles-dir "$HOME\.dbt"
```

## Structure du projet

```text
nyc-taxi-data-engineering/
│
├── data/
│   ├── raw/
│   └── profiling/
│
├── ingestion/
│   └── load_to_snowflake.py
│
├── dbt/
│   ├── models/
│   │   ├── staging/
│   │   ├── intermediate/
│   │   └── final/
│   │
│   ├── macros/
│   ├── tests/
│   ├── dbt_project.yml
│   └── packages.yml
│
├── .github/
│   └── workflows/
│
├── requirements.txt
├── .gitignore
└── README.md
```

## Compétences mobilisées

* Python
* SQL
* Snowflake
* dbt Core
* DuckDB
* Parquet
* Data Quality
* Data Warehouse
* modélisation analytique
* Git / GitHub
* PowerShell
* tests automatisés

## Conclusion

Ce projet reproduit un scénario proche d'un contexte professionnel de Data Engineering : ingestion de données volumineuses, stockage dans un Data Warehouse, transformation par couches, traitement des problèmes de qualité, production de modèles analytiques et validation automatisée.

Le pipeline constitue une base exploitable pour alimenter ensuite un outil de BI ou un système de reporting.
