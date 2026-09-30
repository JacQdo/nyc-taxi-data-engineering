# 🚕 NYC Taxi Data Engineering

Projet de **Data Engineering** réalisé à partir des données **NYC Yellow Taxi** sur la période **2022–2024**.

L'objectif est de construire une chaîne de traitement de données complète, structurée et reproductible, depuis l'ingestion des fichiers Parquet jusqu'à la production de modèles analytiques dans Snowflake.

Le projet met en œuvre une architecture en couches :

```text
RAW → STAGING → INTERMEDIATE → FINAL
```

avec **Python** pour l'ingestion, **Snowflake** pour le stockage et **dbt** pour les transformations et les contrôles de qualité.

---

## 📌 1. Objectifs du projet

Le projet répond à quatre objectifs principaux.

### 1. Ingestion

* Importer les fichiers Parquet NYC Yellow Taxi 2022, 2023 et 2024.
* Charger les données dans Snowflake.
* Conserver les données originales dans une couche RAW.
* Éviter les rechargements inutiles des fichiers déjà traités.

### 2. Transformation

* Standardiser les noms de colonnes.
* Créer les dimensions temporelles nécessaires à l'analyse.
* Calculer la durée des trajets.
* Appliquer des règles de nettoyage métier.

### 3. Data Quality

* Identifier les anomalies présentes dans les données.
* Conserver les anomalies dans RAW afin de préserver les données sources.
* Appliquer les règles de qualité dans la couche INTERMEDIATE.
* Mettre en place des tests automatisés avec dbt.

### 4. Analyse

Produire trois modèles analytiques :

* analyse quotidienne ;
* analyse horaire ;
* analyse par zone de pickup.

---

# 🏗️ 2. Architecture du projet

```text
                    ┌──────────────────────────┐
                    │      Fichiers Parquet    │
                    │    NYC Yellow Taxi       │
                    │        2022–2024         │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │          Python          │
                    │        Ingestion         │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │        Snowflake         │
                    │           RAW            │
                    │       YELLOW_TRIPS       │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │           dbt            │
                    │         STAGING          │
                    │    STG_YELLOW_TAXI       │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │           dbt            │
                    │       INTERMEDIATE       │
                    │      INT_CLEAN_TRIPS     │
                    └────────────┬─────────────┘
                                 │
                 ┌───────────────┼───────────────┐
                 ▼               ▼               ▼
        ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
        │  DAILY_TRIPS   │ │HOURLY_PATTERNS │ │ ZONE_ANALYSIS  │
        └────────────────┘ └────────────────┘ └────────────────┘
                 │               │               │
                 └───────────────┼───────────────┘
                                 ▼
                    ┌──────────────────────────┐
                    │      Data Quality        │
                    │       dbt tests          │
                    └──────────────────────────┘
```

### Principe de séparation des responsabilités

| Composant        | Responsabilité                    |
| ---------------- | --------------------------------- |
| Python           | Ingestion des fichiers            |
| Snowflake RAW    | Conservation des données sources  |
| dbt STAGING      | Standardisation et préparation    |
| dbt INTERMEDIATE | Nettoyage et règles métier        |
| dbt FINAL        | Agrégations analytiques           |
| dbt tests        | Contrôle automatisé de la qualité |

---

# 📂 3. Sources de données

Les données utilisées sont les fichiers **NYC Yellow Taxi** au format Parquet.

### Période

```text
2022
2023
2024
```

### Organisation des données

```text
data/
└── raw/
    └── yellow_taxi/
        ├── 2022/
        ├── 2023/
        └── 2024/
```

Le projet utilise :

* **36 fichiers Parquet**
* **12 fichiers par année**
* environ **1,81 GB** de données compressées

### Volume approximatif

| Année     |       Volume |
| --------- | -----------: |
| 2022      |     ~0,57 GB |
| 2023      |     ~0,59 GB |
| 2024      |     ~0,65 GB |
| **Total** | **~1,81 GB** |

---

# 🐍 4. Ingestion avec Python

L'ingestion est réalisée avec :

```text
ingestion/load_to_snowflake.py
```

Le script réalise les opérations suivantes :

1. parcours des fichiers Parquet ;
2. préparation du chargement ;
3. dépôt des fichiers dans un stage Snowflake ;
4. chargement avec `COPY INTO` ;
5. conversion explicite des timestamps ;
6. chargement dans la table RAW ;
7. ciblage du fichier traité afin d'éviter les rechargements inutiles.

### Ressources Snowflake utilisées

Table RAW :

```text
NYC_TAXI.RAW.YELLOW_TRIPS
```

Stage :

```text
NYC_TAXI.RAW.YELLOW_TAXI_STAGE
```

Format Parquet :

```text
NYC_TAXI.RAW.PARQUET_FORMAT
```

---

# ❄️ 5. Snowflake

## Database

```text
NYC_TAXI
```

## Warehouse

```text
NYC_TAXI_WH
```

Configuration :

```text
Warehouse size : X-SMALL
Auto suspend   : 60 secondes
Auto resume    : TRUE
```

## Schémas

```text
RAW
STAGING
INTERMEDIATE
FINAL
```

Cette séparation permet d'isoler les différentes étapes du traitement.

---

# 🗄️ 6. Couche RAW

La couche RAW constitue le point d'entrée des données dans


Ces tests contrôlnte exactement

📅 pickup entre 2022 et 2024
⏱️ dropoff ≥ pickup
👥 passenger_count > 0 lorsqu'il n'est pas NULL
📏 distance ≤ 200 miles
💰 total_amount ≥ 0
💵 fare_amount ≥ 0
💵 tip_amount ≥ 0
🛣️ tolls_amount ≥ 0
⏱️ durée ≥ 0
⏱️ durée ≤ 1 440 minutes (24 h)