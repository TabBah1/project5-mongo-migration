import os
import pymongo
from dotenv import load_dotenv

load_dotenv()

def setup_rbac():
    # Connexion Admin
    client = pymongo.MongoClient(
        host="localhost",
        port=27017, # Garde 27017 pour l'instant
        username=os.getenv("MONGO_USER"),
        password=os.getenv("MONGO_PASS"),
        authSource="admin"
    )
    db = client["healthcare"]

    # 1. Création de la VUE (Sécurité par Hôpital)
    try:
        db.command({
            "create": "view_sons_miller",
            "viewOn": "patients",
            "pipeline": [{"$match": {"staff.hospital": "Sons and Miller"}}]
        })
        print("[OK] Vue 'Sons and Miller' créée.")
    except:
        print("[INFO] La vue existe déjà.")

    # 2. Création des comptes utilisateurs
    users = [
        {"user": "medical_editor", "pwd": "editor_password123", "roles": [{"role": "readWrite", "db": "healthcare"}]},
        {"user": "medical_viewer", "pwd": "viewer_password123", "roles": [{"role": "read", "db": "healthcare"}]},
        {"user": "doctor_miller", "pwd": "miller_password123", "roles": [{"role": "read", "db": "healthcare", "collection": "view_sons_miller"}]}
    ]

    for u in users:
        try:
            db.command("createUser", u["user"], pwd=u["pwd"], roles=u["roles"])
            print(f"[OK] Utilisateur {u['user']} créé.")
        except:
            print(f"[INFO] Utilisateur {u['user']} déjà présent.")

if __name__ == "__main__":
    setup_rbac()