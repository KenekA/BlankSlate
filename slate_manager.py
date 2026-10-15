# slate_manager.py
# handles saving, loading, and managing the user's slate collection
# think of this as the middleman between your code and the save files

import json
import os

# the folder where all slate files will be stored
SLATES_FOLDER = "slates"

# the file that tracks which slate is currently active
USER_DATA_FILE = "user_data.json"

def initialize():
    # creates the slates folder if it doesn't exist yet
    if not os.path.exists(SLATES_FOLDER):
        os.makedirs(SLATES_FOLDER)
        print("Created slates folder.")

    # creates a default user_data.json if it doesn't exist yet
    if not os.path.exists(USER_DATA_FILE):
        default_user_data = {"active_slate": None}
        save_json(USER_DATA_FILE, default_user_data)
        print("Created user data file.")

def save_json(filepath, data):
    # helper — saves any dictionary to a json file
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)

def load_json(filepath):
    # helper — loads a json file and returns it as a dictionary
    with open(filepath, "r") as f:
        return json.load(f)

def save_slate(slate):
    # saves a slate dictionary to its own json file
    # filename is based on the slate's name, lowercased
    filename = os.path.join(SLATES_FOLDER, f"{slate['name'].lower()}.json")
    save_json(filename, slate)
    print(f"Saved slate: {slate['name']}")

def load_slate(name):
    # loads a slate by name from the slates folder
    # returns the slate as a dictionary, or None if not found
    filename = os.path.join(SLATES_FOLDER, f"{name.lower()}.json")
    if not os.path.exists(filename):
        print(f"No slate found with name: {name}")
        return None
    return load_json(filename)

def get_all_slates():
    # returns a list of all slate names in the collection
    slates = []
    for filename in os.listdir(SLATES_FOLDER):
        if filename.endswith(".json"):
            slates.append(filename.replace(".json", ""))
    return slates

def set_active_slate(name):
    # sets which slate is currently active
    user_data = load_json(USER_DATA_FILE)
    user_data["active_slate"] = name.lower()
    save_json(USER_DATA_FILE, user_data)
    print(f"Active slate set to: {name}")

def get_active_slate():
    # loads and returns the currently active slate
    # returns None if no active slate has been set
    user_data = load_json(USER_DATA_FILE)
    active_name = user_data.get("active_slate")

    if active_name is None:
        print("No active slate set.")
        return None

    return load_slate(active_name)