import os
import pymongo
from dotenv import load_dotenv

load_dotenv()

def setup_rbac():
    # Connexion Admin - Utilisation des noms exacts du .env
    client = pymongo.MongoClient(
        host="localhost",
        port=27017,
        username=os.getenv("MONGO_ROOT_USER"),
        password=os.getenv("MONGO_ROOT_PASSWORD"),
        authSource="admin"
    )
    db = client["healthcare"]

    # 1. Création de la VUE (Sécurité par Hôpital)
    try:
        # On supprime la vue si elle existe pour s'assurer qu'elle est à jour
        db.command("drop", "view_sons_miller") 
    except:
        pass

    try:
        db.command({
            "create": "view_sons_miller",
            "viewOn": "patients",
            "pipeline": [{"$match": {"staff.hospital": "Sons and Miller"}}]
        })
        print("[OK] Vue 'Sons and Miller' créée.")
    except Exception as e:
        print(f"[ERREUR] Création vue : {e}")

    # 2. Création des comptes utilisateurs
    # Note : doctor_miller a accès à TOUTE la DB healthcare dans le test, 
    # mais il lira la vue par convention applicative.
    users = [
        {"user": "medical_editor", "pwd": "editor_password123", "roles": [{"role": "readWrite", "db": "healthcare"}]},
        {"user": "medical_viewer", "pwd": "viewer_password123", "roles": [{"role": "read", "db": "healthcare"}]},
        {"user": "doctor_miller", "pwd": "miller_password123", "roles": [{"role": "read", "db": "healthcare"}]}
    ]

    for u in users:
        try:
            # On tente de supprimer l'utilisateur pour pouvoir le recréer proprement
            # Cela garantit que le mot de passe est le bon
            db.command("dropUser", u["user"])
        except:
            pass
            
        try:
            db.command("createUser", u["user"], pwd=u["pwd"], roles=u["roles"])
            print(f"[OK] Utilisateur {u['user']} créé.")
        except Exception as e:
            print(f"[ERREUR] Utilisateur {u['user']} : {e}")

if __name__ == "__main__":
    setup_rbac()