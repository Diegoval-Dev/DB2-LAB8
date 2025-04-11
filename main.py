import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import json
from bson import ObjectId

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
  raise ValueError("Falta la variable MONGO_URI en el archivo .env")

client = MongoClient(MONGO_URI)
db = client["gercoRaunte"]

print("Paso 1: Insertando restaurantes...")
restaurants_df = pd.read_csv("data/restaurants.csv")
restaurants_df["specialties"] = restaurants_df["specialties"].apply(lambda x: x.split(", "))
restaurants_df["imageIds"] = restaurants_df["imageIds"].apply(lambda x: x.split(", "))

restaurant_records = restaurants_df.to_dict(orient="records")
inserted = db["restaurants"].insert_many(restaurant_records)
restaurant_ids = inserted.inserted_ids
restaurant_name_to_id = dict(zip(restaurants_df["name"], restaurant_ids))

print(f"Insertados {len(restaurant_ids)} restaurantes")

def convert_restaurant_ref(name):
  return restaurant_name_to_id.get(name.strip(), None)

print("Insertando users...")
users_df = pd.read_csv("data/users.csv")
db["users"].delete_many({})
db["users"].insert_many(users_df.to_dict(orient="records"))
print(f"Insertados {len(users_df)} usuarios")

print("Insertando menu_items...")
menu_df = pd.read_csv("data/menu_items.csv")
menu_df["restaurantId"] = menu_df["restaurantId"].apply(convert_restaurant_ref)
db["menu_items"].delete_many({})
db["menu_items"].insert_many(menu_df.to_dict(orient="records"))
print(f"Insertados {len(menu_df)} menú items")

print("Insertando orders...")
orders_df = pd.read_csv("data/orders.csv")
orders_df["restaurantId"] = orders_df["restaurantId"].apply(convert_restaurant_ref)
orders_df["items"] = orders_df["items"].apply(lambda x: json.loads(x.replace("'", '"')))
db["orders"].delete_many({})
db["orders"].insert_many(orders_df.to_dict(orient="records"))
print(f"Insertados {len(orders_df)} órdenes")

print("Insertando reviews...")
reviews_df = pd.read_csv("data/reviews.csv")
reviews_df["restaurantId"] = reviews_df["restaurantId"].apply(convert_restaurant_ref)
db["reviews"].delete_many({})
db["reviews"].insert_many(reviews_df.to_dict(orient="records"))
print(f"Insertados {len(reviews_df)} reseñas")

print("Carga completa. Verifica en MongoDB Atlas.")
client.close()
