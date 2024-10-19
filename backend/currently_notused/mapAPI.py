import requests
from dotenv import load_dotenv
import os
load_dotenv()
MAP_API_KEY = os.getenv("MAP_API_KEY")
class MapHandler():
    def __init__(self):
        pass
    def get_coor(self, address: str):
            map_url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                "address": address,
                "key": MAP_API_KEY
            }
            response = requests.get(map_url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data["status"] == "OK":
                    # get coor
                    location = data["results"][0]["geometry"]["location"]
                    # print("location is:", location["lat"], location["lng"])
                    return location["lat"], location["lng"]
                else:
                    print("Error: ", data["status"])
                    return None
            else:
                print(f"Error: {response.status_code}")
                return None