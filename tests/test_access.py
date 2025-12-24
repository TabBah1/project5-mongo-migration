import pymongo

def check_access(user, pwd, description):
    print(f"\n--- Test pour : {description} ({user}) ---")
    
    # Correction : On essaie d'abord authSource=admin car c'est souvent là que sont stockés les comptes
    try:
        uri = f"mongodb://{user}:{pwd}@localhost:27017/healthcare?authSource=admin"
        client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=2000)
        db = client["healthcare"]
        
        # Test de Lecture
        col = "view_sons_miller" if user == "doctor_miller" else "patients"
        doc = db[col].find_one()
        print(f"Lecture réussie sur '{col}'")
        
    except Exception:
        # Si admin échoue, on tente authSource=healthcare
        try:
            uri = f"mongodb://{user}:{pwd}@localhost:27017/healthcare?authSource=healthcare"
            client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=2000)
            db = client["healthcare"]
            col = "view_sons_miller" if user == "doctor_miller" else "patients"
            doc = db[col].find_one()
            print(f"Lecture réussie sur '{col}' (via authSource=healthcare)")
        except Exception as e:
            print(f"ÉCHEC TOTAL : {e}")

    # Test d'Écriture (si la lecture a réussi)
    try:
        db.patients.update_one({"_id": "test_id"}, {"$set": {"status": "ok"}}, upsert=True)
        print("Écriture autorisée")
        db.patients.delete_one({"_id": "test_id"})
    except:
        print("Écriture refusée (Protection active)")

if __name__ == "__main__":
    check_access("medical_editor", "editor_password123", "ÉDITEUR")
    check_access("medical_viewer", "viewer_password123", "LECTEUR")
    check_access("doctor_miller", "miller_password123", "MÉDECIN")