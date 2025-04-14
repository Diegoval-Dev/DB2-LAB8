import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import json
from bson import ObjectId

# Cargar variables de entorno
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("Falta la variable MONGO_URI en el archivo .env")

client = MongoClient(MONGO_URI)
db = client["gercoRaunte"]

# Función auxiliar para convertir IDs
def to_object_id(value):
    try:
        return ObjectId(str(value))
    except:
        return None

# Cargar restaurantes
print("Insertando restaurantes...")
restaurants_df = pd.read_csv("./data/restaurants_full.csv")
restaurants_df["id"] = restaurants_df["id"].apply(to_object_id)
restaurants_df["specialties"] = restaurants_df["specialties"].apply(lambda x: x.split(",") if isinstance(x, str) else [])
restaurants_df["imageIds"] = restaurants_df["imageIds"].apply(lambda x: x.split(",") if isinstance(x, str) else [])

db["restaurants"].delete_many({})
restaurant_records = restaurants_df.drop(columns=["id"]).to_dict(orient="records")
inserted_restaurants = db["restaurants"].insert_many(restaurant_records)
restaurant_id_map = dict(zip(restaurants_df["id"].astype(str), inserted_restaurants.inserted_ids))

# Cargar usuarios
print("Insertando usuarios...")
users_df = pd.read_csv("./data/users_full.csv")
users_df["id"] = users_df["id"].apply(to_object_id)

db["users"].delete_many({})
user_records = users_df.drop(columns=["id"]).to_dict(orient="records")
inserted_users = db["users"].insert_many(user_records)
user_id_map = dict(zip(users_df["id"].astype(str), inserted_users.inserted_ids))

# Cargar ítems de menú
print("Insertando menú...")
menu_df = pd.read_csv("./data/menu_items_full.csv")
menu_df["id"] = menu_df["id"].apply(to_object_id)
menu_df["restaurantId"] = menu_df["restaurantId"].astype(str).map(restaurant_id_map)
menu_df["restaurantId"] = menu_df["restaurantId"].apply(to_object_id)

db["menu_items"].delete_many({})
menu_records = menu_df.drop(columns=["id"]).to_dict(orient="records")
inserted_menu = db["menu_items"].insert_many(menu_records)
menu_id_map = dict(zip(menu_df["id"].astype(str), inserted_menu.inserted_ids))

# Cargar órdenes
print("Insertando órdenes...")
orders_df = pd.read_csv("./data/orders_full.csv")
orders_df["restaurantId"] = orders_df["restaurantId"].astype(str).map(restaurant_id_map).apply(to_object_id)
orders_df["userId"] = orders_df["userId"].astype(str).map(user_id_map).apply(to_object_id)

def convert_items(val):
    try:
        items = json.loads(val)
        for item in items:
            item["menu_item_id"] = to_object_id(menu_id_map.get(item["menu_item_id"]))
        return items
    except:
        return []

orders_df["items"] = orders_df["items"].apply(convert_items)

db["orders"].delete_many({})
orders_records = orders_df.drop(columns=["id"]).to_dict(orient="records")
db["orders"].insert_many(orders_records)
print(f"Insertadas {len(orders_records)} órdenes")

# Cargar reseñas
print("Insertando reseñas...")
reviews_df = pd.read_csv("./data/reviews_full.csv")
reviews_df["restaurantId"] = reviews_df["restaurantId"].astype(str).map(restaurant_id_map).apply(to_object_id)
reviews_df["userId"] = reviews_df["userId"].astype(str).map(user_id_map).apply(to_object_id)

db["reviews"].delete_many({})
reviews_records = reviews_df.drop(columns=["id"]).to_dict(orient="records")
db["reviews"].insert_many(reviews_records)
print(f"Insertadas {len(reviews_records)} reseñas")

print("✅ Carga completada con éxito.")
client.close()
