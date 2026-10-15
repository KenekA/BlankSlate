# inventory_manager.py
# handles the player's trait inventory
# traits sit here after being dropped from a lootbox
# before being applied to a slate or sold on the market

import json
import os

PLAYERS_FOLDER = "players"

def get_inventory_path(player_id):
    # builds the file path to a player's inventory file
    return os.path.join(PLAYERS_FOLDER, player_id, "inventory.json")

def get_profile_path(player_id):
    # builds the file path to a player's profile file
    return os.path.join(PLAYERS_FOLDER, player_id, "profile.json")

def load_inventory(player_id):
    # loads and returns a player's inventory as a dictionary
    path = get_inventory_path(player_id)
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

def save_inventory(player_id, inventory):
    # saves a player's inventory dictionary back to their json file
    path = get_inventory_path(player_id)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(inventory, f, indent=4)

def load_profile(player_id):
    # loads and returns a player's profile as a dictionary
    path = get_profile_path(player_id)
    if not os.path.exists(path):
        print(f"No profile found for player: {player_id}")
        return None
    with open(path, "r") as f:
        return json.load(f)

def save_profile(player_id, profile):
    # saves a player's profile back to their json file
    path = get_profile_path(player_id)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(profile, f, indent=4)

def create_player(player_id, name="Player", starting_currency=0):
    # sets up a new player's folder, profile, and empty inventory
    # safe to call on every startup: anything that already exists is left alone
    if not os.path.exists(get_profile_path(player_id)):
        save_profile(player_id, {
            "id": player_id,
            "name": name,
            "currency": starting_currency
        })
        print(f"Created new player: {player_id}")

    if not os.path.exists(get_inventory_path(player_id)):
        save_inventory(player_id, {})

def add_trait_to_inventory(player_id, trait_id, stars):
    # adds a dropped trait to the player's inventory
    # stacks duplicates under the same trait_id entry
    # each copy keeps its own star rating
    inventory = load_inventory(player_id)

    if trait_id not in inventory:
        # first copy of this trait — create a new entry
        inventory[trait_id] = {
            "trait_id": trait_id,
            "copies": []
        }

    # add this copy with its star rating
    inventory[trait_id]["copies"].append({"stars": stars})
    save_inventory(player_id, inventory)
    print(f"Added {trait_id} ({stars} stars) to {player_id}'s inventory.")

def remove_trait_from_inventory(player_id, trait_id, stars):
    # removes one specific copy of a trait from inventory
    # matches by star rating — removes the first copy with that star value
    # returns True if successful, False if not found
    inventory = load_inventory(player_id)

    if trait_id not in inventory:
        print(f"Trait {trait_id} not found in inventory.")
        return False

    copies = inventory[trait_id]["copies"]

    for i, copy in enumerate(copies):
        if copy["stars"] == stars:
            copies.pop(i)

            # if no copies remain remove the trait entry entirely
            if len(copies) == 0:
                del inventory[trait_id]

            save_inventory(player_id, inventory)
            print(f"Removed {trait_id} ({stars} stars) from {player_id}'s inventory.")
            return True

    print(f"No copy of {trait_id} with {stars} stars found.")
    return False

def display_inventory(player_id):
    # prints a clean readable summary of the player's inventory
    inventory = load_inventory(player_id)

    if not inventory:
        print("Inventory is empty.")
        return

    print(f"\n--- {player_id}'s inventory ---")
    for trait_id, entry in inventory.items():
        copies = entry["copies"]
        star_list = ", ".join([f"{c['stars']} stars" for c in copies])
        print(f"  {trait_id} x{len(copies)} — [{star_list}]")
    print("------------------------------\n")

def get_currency(player_id):
    # returns how much in game currency the player currently has
    profile = load_profile(player_id)
    return profile["currency"] if profile else 0

def update_currency(player_id, amount):
    # adds or subtracts currency from a player's balance
    # pass negative amount to subtract e.g. -100
    # balance cannot go below zero
    profile = load_profile(player_id)
    if profile is None:
        return
    profile["currency"] = max(0, profile["currency"] + amount)
    save_profile(player_id, profile)
    print(f"{player_id} currency updated to {profile['currency']}")