import os
import unittest
import pandas as pd  # Ajout de pandas pour le test dynamique
from pymongo import MongoClient
from dotenv import load_dotenv

class TestHealthcareMigration(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Configuration initiale avant les tests"""
        load_dotenv()
        cls.mongo_uri = os.getenv("MONGO_URI", "mongodb://admin:admin123@localhost:27017")
        cls.client = MongoClient(cls.mongo_uri)
        cls.db = cls.client["healthcare"] 
        cls.collection = cls.db["patients"]
        cls.sample = cls.collection.find_one()
        # Chemin vers le CSV pour le test dynamique
        cls.csv_path = "data/healthcare_dataset.csv"

    def test_count_documents(self):
        """TEST 1 : Vérifie si le nombre de documents est de 54966"""
        count = self.collection.count_documents({})
        self.assertEqual(count, 54966, f"Erreur ! {count} documents trouvés au lieu de 54966")

    def test_nested_structure(self):
        """TEST 2 : Vérifie la présence de la structure imbriquée 'patient.name'"""
        self.assertIsNotNone(self.sample, "La collection est vide")
        self.assertIn("patient", self.sample, "Le bloc 'patient' est manquant")
        self.assertIn("name", self.sample["patient"], "Le champ 'name' dans 'patient' est manquant")

    def test_billing_type(self):
        """TEST 3 : Vérifie que le montant de facturation est numérique"""
        amount = self.sample.get("billing", {}).get("amount")
        self.assertIsInstance(amount, (int, float), "Le montant n'est pas au format numérique")

    def test_deduplication_integrity(self):
        """TEST 4 (Dynamique) : Vérifie que MongoDB = CSV - Doublons"""
        if not os.path.exists(self.csv_path):
            self.skipTest("Fichier CSV source introuvable pour le test dynamique")
        
        # 1. Analyse dynamique du CSV
        df_raw = pd.read_csv(self.csv_path)
        expected_count = len(df_raw.drop_duplicates())
        
        # 2. Vérification MongoDB
        mongo_count = self.collection.count_documents({})
        
        self.assertEqual(mongo_count, expected_count, 
                         f"Discordance : {mongo_count} en base vs {expected_count} attendus après déduplication")

    @classmethod
    def tearDownClass(cls):
        """Fermeture de la connexion après les tests"""
        cls.client.close()

if __name__ == "__main__":
    unittest.main()