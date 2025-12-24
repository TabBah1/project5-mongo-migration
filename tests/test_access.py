import pymongo

def check_access(user, pwd, description):
    print(f"\n--- Test pour : {description} ({user}) ---")
    
    db = None
    client = None
    success = False

    # Tentative 1 : authSource=admin
    try:
        uri = f"mongodb://{user}:{pwd}@localhost:27017/healthcare?authSource=admin"
        client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=2000)
        # On force un ping pour vérifier l'authentification réelle
        client.admin.command('ping')
        db = client["healthcare"]
        
        col = "view_sons_miller" if user == "doctor_miller" else "patients"
        doc = db[col].find_one()
        print(f"Lecture réussie sur '{col}' (via authSource=admin)")
        success = True
        
    except Exception:
        # Tentative 2 : authSource=healthcare
        try:
            uri = f"mongodb://{user}:{pwd}@localhost:27017/healthcare?authSource=healthcare"
            client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=2000)
            client.admin.command('ping')
            db = client["healthcare"]
            
            col = "view_sons_miller" if user == "doctor_miller" else "patients"
            doc = db[col].find_one()
            print(f"Lecture réussie sur '{col}' (via authSource=healthcare)")
            success = True
        except Exception as e:
            print(f"ÉCHEC TOTAL d'authentification : {e}")
            success = False

    # Test d'Écriture (uniquement si l'authentification a réussi et db est défini)
    if success and db is not None:
        try:
            # On tente une insertion dans la collection patients
            db.patients.update_one(
                {"_id": "test_id"}, 
                {"$set": {"status": "test_security"}}, 
                upsert=True
            )
            print("Écriture autorisée ")
            db.patients.delete_one({"_id": "test_id"})
        except Exception:
            print("Écriture refusée (Protection active )")
    else:
        print("Écriture non testée (car l'utilisateur n'a pas pu se connecter)")

if __name__ == "__main__":
    # Ces identifiants doivent correspondre à ceux créés par setup_security.py
    check_access("medical_editor", "editor_password123", "ÉDITEUR")
    check_access("medical_viewer", "viewer_password123", "LECTEUR")
    check_access("doctor_miller", "miller_password123", "MÉDECIN")