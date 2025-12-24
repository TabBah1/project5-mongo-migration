import pandas as pd
import os

# 1. Gestion dynamique des dossiers (Fonctionne sur Windows ET Docker)
# On cherche le dossier du script, puis on remonte d'un niveau pour trouver /data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "healthcare_dataset.csv")
CLEAN_CSV_PATH = os.path.join(BASE_DIR, "data", "healthcare_dataset_clean.csv")

print(f" Recherche du fichier dans : {CSV_PATH}")

# 2. Vérification de sécurité
if not os.path.exists(CSV_PATH):
    print(f"Erreur : Le fichier source est introuvable à l'adresse {CSV_PATH}")
else:
    # 3. Lecture du fichier
    df = pd.read_csv(CSV_PATH)
    print(f"Dataset chargé : {len(df)} lignes.")

    # 4. Normalisation des noms de colonnes
    # Ici strip() enlève les espaces cachés au début ou à la fin des titres
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # 5. Nettoyage automatique des textes
    # On définit les colonnes qui doivent être propres
    text_cols = ["name", "gender", "blood_type", "medical_condition", "doctor", "hospital", "insurance_provider", "admission_type", "medication", "test_results"]
    
    for col in text_cols:
        if col in df.columns:
            # astype(str) évite les erreurs si une case est vide
            df[col] = df[col].astype(str).str.strip().str.title()

    # 6. Conversion des dates avec sécurité (errors='coerce')
    # Si une date est mal écrite, elle devient "NaT" au lieu de bloquer le script
    df["date_of_admission"] = pd.to_datetime(df["date_of_admission"], errors='coerce')
    df["discharge_date"] = pd.to_datetime(df["discharge_date"], errors='coerce')

    # 7. Nettoyage des montants (Important pour les futurs calculs dans MongoDB)
    df["billing_amount"] = pd.to_numeric(df["billing_amount"], errors='coerce')

    # 8. Sauvegarde du fichier propre
    df.to_csv(CLEAN_CSV_PATH, index=False)
    print(f"Succès ! Fichier nettoyé sauvegardé : {CLEAN_CSV_PATH}")
    
    # Petit aperçu pour vérifier
    print("\nTypes de données finaux :")
    print(df.dtypes.head(10))