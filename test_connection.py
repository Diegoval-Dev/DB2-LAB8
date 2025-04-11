from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
uri = os.getenv("MONGO_URI")
client = MongoClient(uri)

try:
    client.admin.command('ping')
    print("Conectado exitosamente a MongoDB Atlas")
except Exception as e:
    print("Error en la conexión:", e)
