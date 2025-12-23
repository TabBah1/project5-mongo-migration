import pandas as pd
import os

# 1. Utilisation d'un chemin robuste
CSV_PATH = os.path.join("data", "healthcare_dataset.csv")

# 2. Vérification de l'existence du fichier
if not os.path.exists(CSV_PATH):
    print(f" Erreur : Le fichier {CSV_PATH} est introuvable !")
else:
    # 3. Lecture du fichier
    df = pd.read_csv(CSV_PATH)

    print(" Fichier chargé avec succès.")
    
    # 4. Inspection approfondie
    print(f"\nDimensions : {df.shape[0]} lignes et {df.shape[1]} colonnes.")
    
    # Voir les types de colonnes (pour préparer le nettoyage)
    print("\nTypes de données détectés :")
    print(df.dtypes)

    # Vérifier les valeurs manquantes
    print("\nValeurs manquantes par colonne :")
    print(df.isnull().sum())

    # Vérifier les doublons
    print(f"\nNombre de lignes en double : {df.duplicated().sum()}")