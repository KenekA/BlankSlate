# lootbox_manager.py
# handles opening lootboxes and dropping traits into player inventory
# uses drop rates and trait pools defined in lootboxes.json

import json
import os
import random
from inventory_manager import add_trait_to_inventory, update_currency, get_currency
from trait_manager import get_traits_by_tier, roll_stars

LOOTBOXES_FILE = os.path.join("data", "lootboxes.json")

def load_lootboxes():
    # loads all lootbox definitions from lootboxes.json
    with open(LOOTBOXES_FILE, "r") as f:
        return json.load(f)

def get_lootbox(box_id):
    # returns a single lootbox definition by its ID
    lootboxes = load_lootboxes()
    return lootboxes.get(box_id, None)

def roll_tier(drop_rates):
    # randomly selects a tier based on the lootbox's drop rates
    # uses weighted random so rarer tiers drop less often
    tiers =   list(drop_rates.keys())
    weights = list(drop_rates.values())
    return random.choices(tiers, weights=weights, k=1)[0]

def roll_trait(box_id, tier):
    # picks a random trait from the correct pool for this box and tier
    # uses the box specific pool if defined, otherwise draws from full tier
    lootbox = get_lootbox(box_id)
    if lootbox is None:
        print(f"Lootbox {box_id} not found.")
        return None

    specific_pool = lootbox["trait_pools"].get(tier)

    if specific_pool is not None:
        # box has a specific pool for this tier — pick from it
        trait_id = random.choice(specific_pool)
    else:
        # no specific pool — draw from the full tier in traits.json
        tier_traits = get_traits_by_tier(tier)
        if not tier_traits:
            print(f"No traits found for tier: {tier}")
            return None
        trait_id = random.choice(list(tier_traits.keys()))

    return trait_id

def open_lootbox(player_id, box_id):
    # the main function — opens a lootbox for a player
    # checks currency, deducts cost, rolls tier, rolls trait, rolls stars
    # deposits result into player inventory and returns the result
    lootbox = get_lootbox(box_id)
    if lootbox is None:
        print(f"Lootbox {box_id} not found.")
        return None

    # check if player can afford the box
    cost = lootbox["cost"]
    current_currency = get_currency(player_id)
    if current_currency < cost:
        print(f"Not enough currency. Need {cost}, have {current_currency}.")
        return None

    # deduct the cost
    update_currency(player_id, -cost)

    # roll the tier, trait, and stars
    tier     = roll_tier(lootbox["drop_rates"])
    trait_id = roll_trait(box_id, tier)
    if trait_id is None:
        return None
    stars    = roll_stars()

    # deposit into inventory
    add_trait_to_inventory(player_id, trait_id, stars)

    # build and return the result for the UI to display
    result = {
        "box_name": lootbox["name"],
        "tier":     tier,
        "trait_id": trait_id,
        "stars":    stars
    }

    print(f"\n=== LOOTBOX OPENED ===")
    print(f"Box:   {lootbox['name']}")
    print(f"Tier:  {tier.upper()}")
    print(f"Trait: {trait_id}")
    print(f"Stars: {stars}/10")
    print(f"======================\n")

    return result