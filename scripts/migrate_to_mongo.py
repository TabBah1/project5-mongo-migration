import pandas as pd
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# 1. Chargement des variables d'environnement (Sécurité)
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:admin123@localhost:27017")

# 2. Connexion MongoDB
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client["healthcare"]
    collection = db["patients"]
    # Test de connexion
    client.admin.command('ping')
    print(" Connexion MongoDB réussie")
except Exception as e:
    print(f" Erreur de connexion : {e}")
    exit()

# 3. Chargement du CSV nettoyé
# On utilise os.path pour être sûr de trouver le fichier dans Docker
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "healthcare_dataset_clean.csv")

if not os.path.exists(CSV_PATH):
    print(f" Fichier introuvable : {CSV_PATH}")
    exit()

df = pd.read_csv(CSV_PATH)

# Suppressions des boublons
df = df.drop_duplicates()

print(f"CSV chargé : {len(df)} lignes à migrer.")

# 4. Transformation en Schéma Imbriqué (Le coeur de ta mission)
print("Transformation des documents en format imbriqué...")
documents = []

for _, row in df.iterrows():
    doc = {
        "patient": {
            "name": row['name'],
            "age": int(row['age']) if pd.notnull(row['age']) else None,
            "gender": row['gender'],
            "blood_type": row['blood_type']
        },
        "medical": {
            "condition": row['medical_condition'],
            "medication": row['medication'],
            "test_results": row['test_results']
        },
        "admission": {
            "date_admission": pd.to_datetime(row['date_of_admission']),
            "date_discharge": pd.to_datetime(row['discharge_date']),
            "type": row['admission_type'],
            "room_number": int(row['room_number']) if pd.notnull(row['room_number']) else None
        },
        "billing": {
            "insurance": row['insurance_provider'],
            "amount": float(row['billing_amount']) if pd.notnull(row['billing_amount']) else 0.0
        },
        "staff": {
            "doctor": row['doctor'],
            "hospital": row['hospital']
        }
    }
    documents.append(doc)

# 5. Insertion (on vide avant pour éviter les doublons de test)
collection.delete_many({}) 
print(f" Insertion de {len(documents)} documents...")
result = collection.insert_many(documents)

# 6. Création des index (sur les nouveaux champs imbriqués)
collection.create_index("patient.name")
collection.create_index("medical.condition")
collection.create_index("admission.date_admission")

print(f" Migration terminée avec succès ({len(result.inserted_ids)} docs).")
print(" Index créés sur les champs imbriqués.")