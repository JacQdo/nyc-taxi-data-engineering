# Analyse réflexive — Projet NYC Taxi Data Engineering

## 1. Introduction

Ce projet de Data Engineering avait pour objectif de construire une chaîne de traitement complète à partir des données publiques NYC TLC Yellow Taxi sur les années 2022 à 2024.

Le projet m'a permis de travailler sur l'ensemble du cycle de vie d'une donnée : ingestion, stockage, analyse de qualité, transformation, modélisation, tests, documentation et versionnement.

L'architecture finale repose sur Python pour l'ingestion, Snowflake pour le stockage et l'exécution SQL, dbt Core pour l'industrialisation des transformations et Git/GitHub pour le versionnement.

L'approche retenue peut être résumée ainsi :

```text
Parquet local
     ↓
Python / PUT
     ↓
Snowflake Internal Stage
     ↓
RAW
     ↓
STAGING
     ↓
INTERMEDIATE
     ↓
FINAL / MARTS
```

Cette expérience m'a surtout amené à comprendre qu'un projet Data Engineering ne consiste pas uniquement à faire fonctionner un pipeline. Il faut également pouvoir expliquer les choix effectués, identifier les limites des données, contrôler leur qualité et rendre le traitement reproductible.

---

# 2. Difficultés rencontrées et solutions apportées

## 2.1. Gestion d'un volume important de données

La première difficulté a été liée au volume des fichiers Parquet.

Le jeu de données local représente environ 1,81 Go compressés et 36 fichiers couvrant trois années.

Traiter directement l'ensemble des fichiers dans un environnement local aurait pu devenir coûteux en mémoire et moins représentatif d'une architecture Data Warehouse.

### Solution

J'ai séparé les responsabilités :

* Python pour l'ingestion ;
* Snowflake pour le stockage et les traitements SQL ;
* dbt pour les transformations analytiques.

Cette séparation m'a permis de conserver une architecture plus proche d'un contexte professionnel.

---

## 2.2. Problèmes de qualité des données

L'analyse initiale a révélé plusieurs anomalies :

* dates hors période ;
* dates de dropoff antérieures au pickup ;
* valeurs NULL ;
* nombres de passagers incohérents ;
* distances extrêmes ;
* montants négatifs ;
* durées négatives ou excessivement longues.

Une difficulté importante a été de ne pas considérer automatiquement toute anomalie comme une erreur nécessitant une suppression.

Par exemple, une valeur NULL dans `passenger_count` ne signifie pas nécessairement que le trajet est inutilisable.

### Solution

J'ai défini explicitement des règles métier de nettoyage.

Par exemple :

```sql
pickup_datetime >= '2022-01-01'
AND pickup_datetime < '2025-01-01'
```

ainsi que :

```sql
dropoff_datetime >= pickup_datetime
```

et des contrôles sur les montants, distances et durées.

Les règles ont été regroupées dans le modèle :

```text
int_clean_trips
```

Cette approche permet de rendre les décisions de nettoyage explicites et reproductibles.

---

## 2.3. Gestion des timestamps Parquet

Une difficulté technique particulière concernait l'interprétation des timestamps contenus dans les fichiers Parquet lors du chargement Snowflake.

Une conversion explicite a été mise en place afin de garantir une interprétation correcte des timestamps.

### Solution

Le chargement utilise une conversion explicite vers `TIMESTAMP_NTZ`.

Cette étape a permis d'éviter de dépendre uniquement de l'inférence automatique des types et d'avoir une représentation temporelle cohérente dans Snowflake.

---

## 2.4. Configuration de dbt et Snowflake

La configuration de dbt a également demandé plusieurs ajustements.

Il fallait notamment gérer :

* le profil Snowflake ;
* le warehouse ;
* les schémas ;
* les chemins du projet ;
* les dépendances entre modèles ;
* les macros ;
* les tests.

Une attention particulière a été portée à la séparation entre la configuration du projet et les informations sensibles.

### Solution

Le mot de passe Snowflake n'est pas versionné dans Git.

La configuration utilise une variable d'environnement :

```text
SNOWFLAKE_PASSWORD
```

et le fichier contenant les credentials est exclu du dépôt.

Cette expérience m'a sensibilisé à l'importance de la sécurité dès le développement local et pas uniquement au moment du déploiement.

---

## 2.5. Industrialisation des transformations

Au début d'un projet SQL, il est possible de multiplier les scripts indépendants.

Cette approche devient rapidement difficile à maintenir.

### Solution

J'ai structuré les transformations avec dbt :

```text
RAW
 ↓
STAGING
 ↓
INTERMEDIATE
 ↓
FINAL
```

Chaque couche possède une responsabilité claire.

Cela permet également d'utiliser `ref()` pour matérialiser les dépendances entre modèles.

---

## 2.6. Mise en place des tests

Une autre difficulté a été de ne pas considérer le résultat SQL comme suffisant.

Un modèle peut s'exécuter sans erreur tout en produisant des données incorrectes.

### Solution

J'ai ajouté :

* `not_null` ;
* `unique` ;
* un test personnalisé `non_negative` ;
* un test métier global sur `int_clean_trips` ;
* un contrôle de cohérence des mesures des modèles FINAL.

Les modèles FINAL disposent de **13 tests validés** et le modèle INTERMEDIATE de **8 tests validés**.

Cette démarche m'a permis de distinguer :

```text
Le code fonctionne
```

de :

```text
Les données produites respectent les règles attendues
```

---

# 3. Choix techniques et justification

## 3.1. Python pour l'ingestion

Python a été utilisé pour :

* télécharger les données ;
* organiser les fichiers ;
* analyser les données ;
* effectuer les opérations d'ingestion.

Python est particulièrement adapté à l'automatisation des tâches d'ingestion et à l'intégration avec différents systèmes.

La logique métier lourde n'a cependant pas été concentrée dans Python.

---

## 3.2. Snowflake comme Data Warehouse

Snowflake a été choisi pour centraliser les données et exécuter les traitements SQL.

L'utilisation de Snowflake permet notamment de travailler avec :

* un warehouse dédié ;
* des schémas séparés ;
* une couche RAW ;
* des traitements SQL scalables ;
* une séparation entre stockage et calcul.

Le projet
