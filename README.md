# Migration de données médicales vers MongoDB

## Contexte et motivation du projet

Ce projet vise à migrer des données médicales de patients depuis des fichiers CSV vers une base de données MongoDB. L’objectif est de mettre en place une solution fiable, sécurisée et facilement scalable, en s’appuyant sur une architecture conteneurisée.

Le projet s’articule autour de plusieurs éléments clés :

- data : regroupe les jeux de données, aussi bien bruts que nettoyés;

- scripts : contient les scripts Python du pipeline ETL, chargés de l’extraction, de la transformation et du chargement des données;

- tests : rassemble les tests automatisés permettant de vérifier la qualité et l’intégrité des données;

- Configuration Docker : l’orchestration de MongoDB via docker-compose.yml simplifie le déploiement et la gestion de l’environnement.

La migration des données est automatisée à travers un pipeline structuré en trois étapes principales :

1 - Une première phase d’exploration des données avec le script read_csv.py

2 - Le nettoyage et la préparation des données (déduplication, normalisation) grâce à clean_data.py

3 - L’insertion des données dans MongoDB, avec une transformation vers un schéma imbriqué, réalisée par migrate_to_mongo.py

## Technologies et outils

L'architecture technique s'appuie sur Python 3.10 pour l'ensemble du traitement des données et l'automatisation du pipeline. La bibliothèque Pandas a été utilisée pour l'exploration initiale et le nettoyage du dataset, tandis que MongoDB 8.2.3 constitue le cœur de notre solution de stockage NoSQL. La communication entre Python et MongoDB est assurée par PyMongo, le driver officiel. L'infrastructure est entièrement conteneurisée grâce à Docker et Docker Compose, ce qui garantit la reproductibilité de l'environnement. J'ai également utilisé Conda pour la gestion de l'environnement virtuel (nommé project5), et python-dotenv pour une gestion sécurisée des variables d'environnement sensibles.

## Organisation du code et Strucure du projet 

Le projet suit une structure modulaire standard qui facilite la maintenance et l'évolution future. À la racine, on trouve un dossier `data/` contenant les datasets bruts et nettoyés, un dossier `scripts/` qui héberge les différentes étapes du pipeline ETL, et un dossier `tests/` dédié aux tests automatisés. Les scripts principaux incluent `read_csv.py` pour la lecture et l'exploration initiale, `clean_data.py` pour le nettoyage et la normalisation des données, et enfin `migrate_to_mongo.py` qui gère la migration proprement dite vers MongoDB avec un schéma imbriqué. Les fichiers de configuration comme le `.env` (pour les secrets), le `docker-compose.yml`, le `Dockerfile` et le `requirements.txt` complètent cette architecture.

- Structure du projet: 
```PROJECT5-MONGO-MIGRATION/
├── .vscode/                # Configuration de l'éditeur
│   └── settings.json
├── data/                   # Datasets (healthcare_dataset_clean.csv, etc.)
├── scripts/                # Pipeline ETL et Configuration
│   ├── clean_data.py       # Nettoyage des données avec Pandas
│   ├── migrate_to_mongo.py # Transformation et injection NoSQL
│   ├── read_csv.py         # Exploration initiale du dataset
│   └── setup_security.py   # Création des rôles et des vues (RBAC)
├── tests/                  # Validation et Audit de sécurité
│   ├── test_access.py      # Vérification des droits (Éditeur, Lecteur, Médecin)
│   └── test_mongo_data.py  # Tests unitaires d'intégrité des documents
├── .env                    # Secrets (URI, Identifiants) - [IGNORÉ PAR GIT]
├── .env.example            # Modèle de configuration pour les autres développeurs
├── .gitignore              # Liste des fichiers à ne pas envoyer sur GitHub
├── docker-compose.yml      # Orchestration du container MongoDB 8.2.3
├── Dockerfile              # Personnalisation de l'image MongoDB
├── README.md               # Documentation complète du projet
└── requirements.txt        # Liste des bibliothèques (pandas, pymongo, python-dotenv)


## Caractéristiques du dataset

Le dataset médical sur lequel j'ai travaillé contient initialement 55 500 entrées, ramenées à 54 966 lignes uniques après une phase de déduplication. Chaque ligne comporte 15 colonnes décrivant des informations essentielles sur les patients : leur identité (nom, âge), des données médicales (condition, médicaments, résultats de tests), des informations administratives (date d'admission, type d'admission, numéro de chambre), ainsi que des données financières et de personnel soignant. La colonne `date_of_admission`, initialement au format string, a été convertie en type date pour faciliter les requêtes temporelles ultérieures.

## Modélisation pour MongoDB

L'un des choix architecturaux majeurs de ce projet concerne la modélisation des données. Plutôt que de répliquer la structure plate du CSV, j'ai opté pour un modèle imbriqué (Embedded Documents) qui tire pleinement parti de la flexibilité de MongoDB. Cette approche consiste à regrouper les informations logiquement liées dans des sous-objets, ce qui présente plusieurs avantages significatifs en termes de performance et de lisibilité.

Concrètement, chaque document de la collection '`patients` est structuré en cinq sous-objets principaux. Le sous-objet `patient` regroupe les informations d'identité (nom, âge, genre, groupe sanguin), tandis que `medical` contient les données cliniques (condition, médication, résultats de tests). Les détails administratifs sont rassemblés dans `admission` (date, type d'admission, numéro de chambre), les informations financières dans `billing` (assurance, montant), et enfin les données du personnel dans `staff` (médecin référent, hôpital).

Cette modélisation imbriquée permet d'accéder à l'ensemble des informations d'un patient en une seule opération de lecture, ce qui optimise considérablement les performances par rapport à des jointures multiples dans un système relationnel classique.

- Structure du JSON: 
 ```{
  "_id": ObjectId("..."),
  "patient": {
    "name": "Liam...",
    "age": 30,
    "gender": "Male",
    "blood_type": "B-"
  },
  "medical": {
    "condition": "Cancer",
    "medication": "Paracetamol",
    "test_results": "Normal"
  },
  "admission": {
    "date_admission": "2024-01-31",
    "type": "Urgent",
    "room_number": 328
  },
  "billing": {
    "insurance": "Blue Cross",
    "amount": 18856.28
  },
  "staff": {
    "doctor": "Matthew Smith",
    "hospital": "Sons And Miller"
  }
}
Grâce au schéma imbriqué et aux index, le système reste ultra-rapide : il accède directement au dossier complet d'un patient sans avoir besoin de fouiller dans toute la base de données.

## Le pipeline de migration

Le processus de migration suit une logique ETL (Extract, Transform, Load) décomposée en plusieurs étapes automatisées. La première phase de nettoyage, implémentée dans `clean_data.py`, normalise les noms de colonnes en snake_case, convertit les types de données appropriés et formate correctement les dates. Cette étape inclut également la déduplication qui a permis d'identifier et de supprimer 534 doublons basés sur les identifiants uniques des patients.

La migration proprement dite, orchestrée par `migrate_to_mongo.py`, transforme les lignes "plates" du CSV en dictionnaires imbriqués conformes au schéma MongoDB défini. L'insertion est effectuée par lots via la méthode `insert_many`, ce qui optimise significativement le temps de chargement comparé à des insertions unitaires.

Pour garantir des performances optimales lors des requêtes futures, j'ai mis en place une stratégie d'indexation automatique. Quatre index ont été créés sur les champs les plus fréquemment interrogés : `patient.name`, `medical.condition`, `admission.date_admission`, ainsi qu'un index composé pour les requêtes multi-critères. Ces index permettent d'accélérer drastiquement les recherches sur un volume de près de 55 000 documents.

La fiabilité du pipeline est assurée par une suite de tests unitaires développée avec le framework `unittest`. Ces tests vérifient automatiquement le chargement complet des 54 966 documents et la conformité du schéma NoSQL. Les quatre tests implémentés valident respectivement le nombre de documents insérés, la structure des sous-objets, la présence des index et l'absence de doublons.

## Sécurité et bonnes pratiques

La sécurité a été une préoccupation constante tout au long du développement. La base MongoDB est protégée par une authentification utilisateur, et l'URL de connexion ainsi que les identifiants sont isolés dans un fichier `.env` qui est explicitement exclu du versioning Git via `.gitignore`. Cette pratique évite toute exposition accidentelle de données sensibles dans le dépôt de code.

Le script de migration a été conçu pour être idempotent : il vide systématiquement la collection cible avant chaque nouvelle insertion, ce qui permet de relancer le pipeline autant de fois que nécessaire sans créer de doublons ou d'incohérences. Cette approche facilite grandement les phases de développement et de débogage.

- Gestion des Accès (RBAC)
Le projet implémente une gestion fine des droits via MongoDB :
* **Admin** : Accès total à l'infrastructure.
* **Medical Editor** : Droits de lecture et écriture sur la base.
* **Medical Viewer** : Lecture seule pour les analyses globales.
* **Doctor Restricted** : Accès limité via une **Vue Filtrée** (ne voit que son propre hôpital).

## Déploiement et mise en œuvre

Pour utiliser ce projet, il suffit de disposer de Docker Desktop et d'un environnement Conda. Après avoir cloné le dépôt et activé l'environnement avec `conda activate project5`, on lance d'abord la base de données via `docker-compose up -d`, puis on installe les dépendances Python listées dans `requirements.txt`. Le pipeline complet s'exécute ensuite en deux commandes successives : d'abord le nettoyage des données avec `python scripts/clean_data.py`, puis la migration avec `python scripts/migrate_to_mongo.py`. La validation finale s'effectue en lançant la suite de tests avec `python -m unittest discover tests`.

- Procedure :

Prérequis:
- Docker Desktop installé.

- Environnement Conda activé : conda activate project5.

## 1. Installation
Lancer la base de données :

docker-compose up -d

- Configuration des variables d'environnement
Créez un fichier `.env` à la racine du projet en vous basant sur `.env.example`. 
Ce fichier doit impérativement contenir l'URI de connexion pour la migration initiale :

`MONGO_URI=mongodb://admin:admin123@localhost:27017/healthcare?authSource=admin`

## 2. Installer les dépendances :

pip install -r requirements.txt

## 3. Exécuter le pipeline :

python scripts/clean_data.py
python scripts/migrate_to_mongo.py
python scripts/setup_security.py

## 4. Lancer les tests de validation :

  - Pour tester les données (Unittest)
python -m unittest tests/test_mongo_data.py

  - Pour tester la sécurité (RBAC)
python tests/test_access.py


## Bilan et perspectives

Ce projet représente une mise en pratique complète des compétences essentielles d'un Data Engineer moderne. J'ai pu démontrer ma capacité à traiter un volume significatif de données (près de 55 000 documents), à concevoir une modélisation NoSQL optimisée, et à sécuriser une infrastructure conteneurisée de bout en bout.

Les résultats concrets incluent le traitement et le nettoyage d'un dataset volumineux avec Python et Pandas, la conception d'une architecture documentaire exploitant pleinement les capacités de MongoDB, l'implémentation d'une stratégie d'indexation pour des performances optimales, et la mise en place d'une infrastructure Docker garantissant l'isolation et la persistance des données (321,1 MB de stockage dans des volumes Docker). La qualité du code est assurée par une couverture complète de tests automatisés, tous validés avec succès.

Ce travail constitue une base solide pour des développements futurs, qu'il s'agisse de traitements Big Data plus complexes ou d'une mise en production sur le cloud. Il m'a également permis de me familiariser en profondeur avec les technologies clés du métier de Data Engineer : MongoDB pour le NoSQL, Docker pour la conteneurisation, Python pour l'automatisation, et les services cloud AWS pour la scalabilité.