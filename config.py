import json
import os

try:
    f = open("config.json")
    data = json.load(f)
    f.close()
except Exception as error:
    print(error)
    data = {
        "MONGO_USER": os.environ["MONGO_USER"],
        "MONGO_PASSWORD": os.environ["MONGO_PASSWORD"]
    }