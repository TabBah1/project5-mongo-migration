import pymongo
import os
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()
client = pymongo.MongoClient(os.getenv("MONGO_URI"))
db = client["healthcare"]
col = db["patients"]

# On lance l'explain via Python
stats = col.find({"patient.name": "Leslie Terry"}).explain()

print("\n--- RÉSULTAT DE L'ANALYSE D'INDEX ---")
print(f"Stage : {stats['queryPlanner']['winningPlan']['stage']}")
print(f"Documents examinés : {stats['executionStats']['totalDocsExamined']}")
print(f"Temps d'exécution : {stats['executionStats']['executionTimeMillis']} ms")