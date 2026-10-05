**README GitHub / portfolio**.

## 1. Positionnement du projet

> ### NYC Taxi Data Engineering — End-to-End Data Platform
>
> Conception et réalisation d'une plateforme Data Engineering complète permettant d'ingérer, nettoyer, transformer, tester et analyser plusieurs dizaines de millions de trajets de taxis new-yorkais.
>
> Le projet met en œuvre une architecture moderne **RAW → STAGING → INTERMEDIATE → FINAL**, avec **Snowflake** comme Data Warehouse, **dbt** pour les transformations et tests, **Python** pour les contrôles de qualité et **Streamlit** pour la restitution BI.
>
> L'objectif est de transformer des données brutes de transport en **indicateurs fiables et exploitables** pour analyser les volumes, le chiffre d'affaires, les périodes de forte activité et les performances opérationnelles.

---

# 2. Architecture

```text
                    NYC TAXI DATA
                         │
                         ▼
                  ┌─────────────┐
                  │     RAW     │
                  │ Snowflake   │
                  └──────┬──────┘
                         │
                         ▼
                ┌──────────────────┐
                │     STAGING      │
                │ Nettoyage /     │
                │ standardisation │
                └────────┬─────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │     INTERMEDIATE     │
              │  INT_CLEAN_TRIPS     │
              │                      │
              │ • dates              │
              │ • distances          │
              │ • durée              │
              │ • vitesse            │
              │ • revenus            │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │        FINAL         │
              │      Data Marts      │
              │                      │
              │ DAILY_TRIPS          │
              │ HOURLY_PATTERNS      │
              │ ZONE_ANALYSIS        │
              │ MEASURES_QUALITY     │
              └──────────┬───────────┘
                         │
             ┌───────────┴───────────┐
             ▼                       ▼
      ┌──────────────┐        ┌──────────────┐
      │   Python     │        │  Streamlit   │
      │ Validation   │        │   Dashboard  │
      └──────────────┘        └──────────────┘
```

### Stack technique

| Domaine        | Technologie                 |
| -------------- | --------------------------- |
| Langage        | Python                      |
| Data Warehouse | Snowflake                   |
| Transformation | dbt Core                    |
| SQL            | Snowflake SQL               |
| Data Quality   | dbt tests + Python          |
| BI / Dashboard | Streamlit                   |
| Versioning     | Git / GitHub                |
| Environnement  | Windows + VS Code + `.venv` |

---

# 3. Chiffres clés du projet

Ce sont les chiffres qui donnent immédiatement de la crédibilité au portfolio.

### Dataset

* **100,319,438** lignes chargées dans RAW
* **97,643,478** trajets conservés après nettoyage
* **2,675,960** lignes rejetées
* environ **2.67 %** de rejets
* période analysée : **2022 → 2024**
* **920 jours** analysés

### Data Warehouse

| Data mart         | Lignes |
| ----------------- | -----: |
| `DAILY_TRIPS`     |    920 |
| `HOURLY_PATTERNS` |     48 |
| `ZONE_ANALYSIS`   |  1,048 |

Les trois marts sont cohérents et représentent chacun les mêmes **97,643,478 trajets** au niveau agrégé.

---

# 4. Data Quality

Une partie importante du projet est la **fiabilisation des données**.

Les règles appliquées comprennent notamment :

* exclusion des dates hors période ;
* suppression des trajets avec dates incohérentes ;
* exclusion des montants financiers négatifs ;
* exclusion des distances négatives ou > 200 km ;
* contrôle des durées invalides ;
* contrôle des vitesses irréalistes ;
* contrôle des taux de pourboire ;
* contrôle des valeurs NULL critiques ;
* contrôles de cohérence entre les différents data marts.

### Résultat

**22/22 tests dbt PASS**

et les contrôles Python :

```text
NEGATIVE_TRIPS        PASS
NEGATIVE_REVENUE      PASS
NEGATIVE_DISTANCE     PASS
INVALID_AVG_DISTANCE  PASS
INVALID_AVG_DURATION  PASS
INVALID_AVG_SPEED     PASS
INVALID_TIP_RATE      PASS
NULL_PICKUP_DATE      PASS
NULL_TRIP_COUNT       PASS
NULL_REVENUE          PASS

RESULTAT GLOBAL : PASS
```

C'est un point à mettre fortement en avant dans ton portfolio : **le dashboard ne repose pas directement sur des données brutes non contrôlées.**

---

# 5. KPI métier

Les données nettoyées permettent de produire les principaux indicateurs suivants :

| KPI                     |       Résultat |
| ----------------------- | -------------: |
| Courses                 |    **97.64 M** |
| Chiffre d'affaires      |  **$2.543 Md** |
| CA moyen / course       |     **$26.04** |
| Distance moyenne        |    **3.45 km** |
| Durée moyenne           |  **17.39 min** |
| Vitesse moyenne         | **11.42 km/h** |
| Taux de pourboire moyen |    **19.67 %** |

---

# 6. Insights analytiques

### Journée record

Le **13 décembre 2024** constitue la journée avec le plus grand nombre de courses :

**155,548 courses**

soit environ **+46.6 %** par rapport à la moyenne quotidienne.

Le chiffre d'affaires atteint :

**$4.58 M**

avec un CA moyen de **$29.46 par course**.

---

### Heure de pointe

L'heure présentant le plus gros volume est :

**18h → 6.95 millions de courses**

sur l'ensemble de la période 2022–2024.

Cependant, le pic de chiffre d'affaires se situe légèrement plus tôt :

**17h → $179.13 M**

Cette distinction est intéressante : **l'heure de plus forte demande n'est pas nécessairement celle qui génère le plus de revenu.**

---

### Périodes de la journée

| Période    | Courses |
| ---------- | ------: |
| Après-midi | 35.33 M |
| Soirée     | 33.18 M |
| Matin      | 21.41 M |
| Nuit       |  7.72 M |

L'après-midi représente donc la période de plus forte activité.

La nuit présente toutefois la distance moyenne la plus élevée :

**3.96 km**

---

### Semaine vs week-end

|          | Courses | CA/course |    Vitesse |
| -------- | ------: | --------: | ---------: |
| Semaine  | 71.04 M |    $26.21 | 12.82 km/h |
| Week-end | 26.61 M |    $25.59 | 13.82 km/h |

On observe notamment que les trajets sont légèrement plus rapides le week-end malgré un volume nettement inférieur.

---

# 7. Dashboard

Le projet dispose maintenant d'une interface Streamlit organisée autour de trois vues :

### 🏠 Executive

Vue destinée à une lecture rapide :

* volume total ;
* chiffre d'affaires ;
* CA/course ;
* distance moyenne ;
* durée ;
* vitesse ;
* évolution quotidienne.

### 💰 Revenue

Analyse économique :

* CA total ;
* CA/course ;
* évolution mensuelle ;
* évolution quotidienne ;
* top journées ;
* CA par période de la journée.

### 🚦 Operations

Analyse opérationnelle :

* journée record ;
* heure de pointe ;
* volume par heure ;
* performance horaire ;
* semaine vs week-end ;
* insights opérationnels.

**Je mettrais 2 ou 3 captures d'écran du dashboard dans le README.** C'est beaucoup plus convaincant qu'une longue explication.

---

# 8. Structure GitHub recommandée

Ton repository peut être présenté ainsi :

```text
nyc-taxi-data-engineering/
│
├── dbt/
│   ├── models/
│   │   ├── staging/
│   │   ├── intermediate/
│   │   └── final/
│   │
│   ├── tests/
│   ├── macros/
│   ├── dbt_project.yml
│   └── profiles.yml
│
├── scripts/
│   ├── validate_peak_day.py
│   ├── validate_peak_hour.py
│   ├── validate_periods.py
│   ├── validate_day_type.py
│   ├── validate_zones.py
│   └── validate_quality.py
│
├── streamlit_app/
│   ├── app.py
│   └── .streamlit/
│       └── secrets.toml
│
├── data/
│   └── profiling/
│
├── docs/
│   ├── architecture.drawio
│   ├── data_dictionary.md
│   └── KPIs.md
│
├── README.md
├── .gitignore
└── requirements.txt
```

⚠️ `secrets.toml`, `profiles.yml` contenant des secrets et les données brutes ne doivent évidemment **pas être commités**.

---

# 9. Une phrase forte pour ton CV

Je te conseille cette formulation :

> **Conception d'une plateforme Data Engineering end-to-end sur 100 M+ de trajets NYC Taxi : ingestion et nettoyage dans Snowflake, transformations SQL avec dbt, data marts analytiques, tests de qualité automatisés avec dbt/Python et dashboard Streamlit pour le pilotage des KPI opérationnels et financiers.**

Et pour ton portfolio :

> **100 M+ lignes | Snowflake | dbt | Python | SQL | Streamlit | Data Quality | Analytics**

---

## 10. Ce que je ferais maintenant

Ton projet est techniquement suffisamment abouti pour passer à la **phase de packaging portfolio**.

Il reste surtout **4 livrables** à finaliser :

1. `README.md` professionnel et complet
2. `architecture.drawio`
3. `data_dictionary.md`
4. `KPIs.md`

Puis une **présentation PowerPoint de 8–10 slides** pour pouvoir présenter le projet en entretien.

Le plus important maintenant est de ne plus ajouter inutilement de fonctionnalités : **il faut transformer le travail technique réalisé en preuve claire de tes compétences de Data Engineer.**
