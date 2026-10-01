# Analyse réflexive — Projet NYC Taxi Data Engineering

## 1. Introduction

Ce projet avait pour objectif de construire un pipeline Data Engineering permettant d'exploiter des données NYC Yellow Taxi sur les années 2022 à 2024.

L'objectif n'était pas uniquement de charger des données dans un Data Warehouse, mais de mettre en œuvre une chaîne complète : ingestion, stockage RAW, standardisation, nettoyage, enrichissement, modélisation analytique et contrôle qualité.

L'architecture retenue repose principalement sur Python, Snowflake, dbt, DuckDB et Git/GitHub.

---

## 2. Difficultés rencontrées et solutions apportées

### 2.1. Volume des données

Le premier défi a été le volume des fichiers Parquet. Le projet représente plusieurs dizaines de fichiers et plus de cent millions de lignes.

Une approche consistant à traiter toutes les données directement en mémoire avec Python aurait été peu adaptée.

J'ai donc séparé les responsabilités :

* Python pour l'ingestion ;
* Snowflake pour le stockage et le traitement SQL ;
* dbt pour les transformations.

Cette organisation m'a permis de conserver une architecture adaptée à un contexte Data Engineering.

### 2.2. Problèmes de qualité des données

L'analyse initiale a montré plusieurs anomalies :

* dates hors période ;
* dates de dropoff antérieures au pickup ;
* montants négatifs ;
* durées négatives ;
* distances aberrantes ;
* valeurs manquantes pour le nombre de passagers ;
* valeurs extrêmes sur certains indicateurs.

Plutôt que de supprimer toutes les lignes présentant une anomalie quelconque, j'ai défini des règles explicites.

Le nettoyage conserve ainsi 97 643 478 lignes sur 100 319 438, soit un taux de conservation de 97,33 % et un taux de rejet de 2,67 %.

Cette quantification permet de justifier les transformations au lieu de présenter le nettoyage comme une opération arbitraire.

### 2.3. Gestion des valeurs manquantes

`passenger_count` contient un nombre important de valeurs NULL.

J'ai choisi de conserver ces valeurs plutôt que de les remplacer artificiellement.

Ce choix repose sur une distinction importante en Data Engineering : une valeur manquante n'est pas nécessairement une valeur invalide.

La conséquence est que les indicateurs qui utilisent cette colonne doivent tenir compte de ce comportement.

### 2.4. Construction des indicateurs

La création de `speed_kmh` et `tip_rate` a nécessité des contrôles supplémentaires.

Certaines valeurs produisaient des résultats extrêmes. J'ai donc défini des bornes analytiques :

* vitesse maximale de 120 km/h ;
* taux de pourboire maximal de 100 %.

Les valeurs dépassant ces seuils sont conservées comme données sources mais ne sont pas utilisées comme indicateurs analytiques valides.

Cette distinction entre donnée source et indicateur analytique constitue un apprentissage important.

### 2.5. Tests dbt

Une difficulté importante est apparue lorsque le grain des modèles finaux a évolué.

Par exemple, `hourly_patterns` n'était plus unique sur `pickup_hour` seul, puisqu'il existe plusieurs types de jours.

La règle correcte est devenue :

```text
pickup_hour + day_type
```

De même, `zone_analysis` doit être unique sur :

```text
pickup_location_id + distance_category
```

J'ai donc créé un test générique `unique_combination`.

Une dépréciation dbt concernant les arguments des generic tests est également apparue. Elle a été corrigée en plaçant les arguments sous la clé `arguments`.

La validation finale donne :

```text
22 tests
22 PASS
0 WARN
0 ERROR
```

Cette étape a renforcé ma compréhension de l'importance du grain d'un modèle analytique et de la nécessité d'aligner les tests sur ce grain.

---

## 3. Choix techniques et justification

### Python

Python a été utilisé pour l'ingestion et la préparation du chargement.

Il est adapté à l'automatisation des opérations répétitives et permet de contrôler le processus de chargement des fichiers Parquet.

### Snowflake

Snowflake constitue le Data Warehouse du projet.

Il permet de séparer clairement :

```text
RAW
STAGING
INTERMEDIATE
FINAL
```

et d'exécuter les transformations SQL sur un volume important de données.

### Internal Stage

J'ai retenu un Internal Stage Snowflake pour le chargement des fichiers.

L'architecture est donc :

```text
Parquet
→ PUT
→ Internal Stage
→ COPY INTO
→ RAW
```

Ce choix permet de rester dans l'écosystème Snowflake tout en automatisant l'ingestion.

### dbt

dbt a été utilisé pour les transformations, la modélisation et les tests.

Ce choix permet notamment :

* de versionner le SQL ;
* de documenter les modèles ;
* de gérer les dépendances avec `ref()` ;
* d'automatiser les tests ;
* de séparer les couches du Data Warehouse.

Le projet illustre donc une utilisation de dbt comme couche de transformation et de qualité plutôt que comme simple outil SQL.

### DuckDB

DuckDB a été utilisé pour les contrôles exploratoires locaux.

Il constitue un outil pratique pour analyser rapidement les fichiers Parquet sans devoir charger immédiatement l'intégralité des données dans Snowflake.

### Git/GitHub

Git permet de conserver l'historique du développement et GitHub permet de présenter le projet comme un livrable professionnel.

La séparation entre code, configuration et secrets constitue également un point important.

---

## 4. Compétences acquises

Ce projet m'a permis de renforcer mes compétences dans plusieurs domaines.

### Data Engineering

J'ai travaillé sur une chaîne complète :

```text
Ingestion
→ Data Warehouse
→ Transformation
→ Qualité
→ Modélisation
→ Tests
```

### SQL

J'ai approfondi :

* CTE ;
* agrégations ;
* fonctions de date ;
* fonctions analytiques ;
* filtrage ;
* transformations conditionnelles ;
* création de modèles analytiques.

### Snowflake

J'ai travaillé avec :

* database ;
* schemas ;
* warehouse ;
* internal stage ;
* file format ;
* COPY INTO ;
* tables ;
* views.

### dbt

J'ai développé ma compréhension de :

* `ref()` ;
* `source()` ;
* materializations ;
* macros ;
* tests génériques ;
* tests SQL ;
* documentation ;
* organisation des modèles par couches.

### Data Quality

Le projet m'a également appris à ne pas considérer la qualité comme une étape secondaire.

Les anomalies doivent être :

1. identifiées ;
2. quantifiées ;
3. interprétées ;
4. traitées selon des règles explicites ;
5. vérifiées par des tests.

---

## 5. Compétences à approfondir

Plusieurs axes restent à approfondir pour rapprocher encore davantage le projet d'une architecture de production.

### Orchestration

L'orchestration pourrait être renforcée avec un véritable workflow permettant de gérer :

* dépendances ;
* reprises ;
* planification ;
* logs ;
* alertes.

### CI/CD

Le projet possède une structure GitHub Actions, mais l'industrialisation pourrait être approfondie avec une pipeline exécutant automatiquement :

```text
Lint
→ dbt compile
→ dbt test
→ validation
→ déploiement
```

### Infrastructure as Code

Une étape supplémentaire consisterait à gérer Snowflake avec Terraform ou un autre outil d'Infrastructure as Code.

### Observabilité

Dans un contexte professionnel, il serait intéressant d'ajouter :

* monitoring des volumes ;
* suivi des temps d'exécution ;
* alertes ;
* suivi des erreurs d'ingestion ;
* détection des dérives de qualité.

### Sécurité

La gestion des secrets pourrait également être industrialisée avec un gestionnaire de secrets plutôt qu'avec une variable d'environnement locale.

---

## 6. Parallèle avec un contexte professionnel réel

Le projet reproduit plusieurs problématiques rencontrées dans une équipe Data.

Dans un environnement professionnel, les données arrivent rarement parfaitement propres. Le Data Engineer doit être capable de distinguer :

* une anomalie réelle ;
* une valeur manquante ;
* une valeur inhabituelle mais acceptable ;
* une valeur incompatible avec l'analyse.

La séparation RAW / STAGING / INTERMEDIATE / FINAL permet également de conserver une traçabilité entre la donnée source et la donnée analytique.

Le projet met aussi en évidence l'importance du grain d'un modèle.

Une table analytique doit avoir une définition précise de ce que représente une ligne. Les tests d'unicité doivent ensuite correspondre exactement à cette définition.

C'est ce qui a conduit à utiliser :

```text
daily_trips
→ pickup_date
```

```text
hourly_patterns
→ pickup_hour + day_type
```

```text
zone_analysis
→ pickup_location_id + distance_category
```

Cette expérience est directement transposable à des projets de reporting, de BI et de Data Warehouse.

---

## 7. Bilan personnel

La principale évolution apportée par ce projet est le passage d'une logique de simple traitement de données à une logique de pipeline Data Engineering.

Je ne me suis pas limité à obtenir un résultat SQL. J'ai dû réfléchir à :

* l'architecture ;
* la volumétrie ;
* la qualité ;
* la traçabilité ;
* les règles métier ;
* le grain des tables ;
* les tests ;
* la reproductibilité ;
* la sécurité des informations de connexion.

Le résultat final est un pipeline organisé en plusieurs couches et validé par des tests automatisés.

La prochaine étape consiste principalement à renforcer l'industrialisation : orchestration, CI/CD, observabilité, gestion des secrets et Infrastructure as Code.

Ce projet constitue ainsi une base concrète pour aborder des problématiques de Data Engineering rencontrées dans un environnement professionnel.
