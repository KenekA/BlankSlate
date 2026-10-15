# trait_manager.py
# handles loading traits from the master traits document
# and applying/combining traits onto a slate

import json
import os
import random

TRAITS_FILE = os.path.join("data", "traits.json")

# the maximum stars a single trait can reach
STAR_CAP = 10

# drop chance (%) for each star rating, index 0 = 1 star ... index 9 = 10 stars
# stars 1-9 drop in a straight line (20% down to 2%, 2.25 per step), 10 stars = 1%
# must contain exactly STAR_CAP entries
STAR_WEIGHTS = [20, 17.75, 15.5, 13.25, 11, 8.75, 6.5, 4.25, 2, 1]

def load_all_traits():
    # loads the full nested traits dictionary from traits.json
    # structure is: { "red": { "red_001": {...}, ... }, "gold": {...}, ... }
    with open(TRAITS_FILE, "r") as f:
        return json.load(f)

def get_trait_by_id(trait_id):
    # extracts the tier from the ID e.g. "red_001" -> "red"
    # then navigates directly to the right section
    all_traits = load_all_traits()
    tier = trait_id.split("_")[0]
    return all_traits.get(tier, {}).get(trait_id, None)

def get_traits_by_tier(tier):
    # returns all traits belonging to a specific tier
    # useful for lootbox rolling
    all_traits = load_all_traits()
    return all_traits.get(tier, {})

def get_all_traits_flat():
    # returns every trait in a single flat dictionary regardless of tier
    # useful when searching across all tiers at once
    all_traits = load_all_traits()
    flat = {}
    for tier_traits in all_traits.values():
        flat.update(tier_traits)
    return flat

def roll_stars():
     # weighted random star rating from 1 to STAR_CAP
    # low stars are common, high stars are rare
    stars = list(range(1, STAR_CAP + 1))
    return random.choices(stars, weights=STAR_WEIGHTS, k=1)[0]

def apply_trait_to_slate(slate, trait_id, incoming_stars):
    # check for a conflicting white tier trait before applying
    # e.g. can't have both "Likes broccoli" and "Dislikes broccoli"
    conflict_id = get_conflicting_trait_id(slate, trait_id)
    if conflict_id is not None:
        conflict_data = get_trait_by_id(conflict_id)
        conflict_name = conflict_data["name"] if conflict_data else conflict_id
        incoming_data = get_trait_by_id(trait_id)
        incoming_name = incoming_data["name"] if incoming_data else trait_id
        print(f"Conflict! Can't apply '{incoming_name}' — slate already has '{conflict_name}'.")
        print(f"Remove '{conflict_name}' first if you want to apply '{incoming_name}'.")
        return slate  # return unchanged

    # check if this trait already exists on the slate — if so combine stars
    for existing_trait in slate["traits"]:
        if existing_trait["trait_id"] == trait_id:
            old_stars = existing_trait["stars"]
            combined_stars = old_stars + incoming_stars
            existing_trait["stars"] = min(combined_stars, STAR_CAP)
            print(
                f"Combined! {trait_id} went from "
                f"{old_stars} to {existing_trait['stars']} stars "
                f"(cap: {STAR_CAP})"
            )
            return slate

    # trait not on slate yet — add it fresh
    slate["traits"].append({
        "trait_id": trait_id,
        "stars": incoming_stars
    })
    print(f"Added new trait: {trait_id} at {incoming_stars} stars")
    return slate

def get_conflicting_trait_id(slate, incoming_trait_id):
    # checks if a slate already has a conflicting white tier trait
    # a conflict is when the same subject exists with a different preference
    # e.g. trying to add "Dislikes broccoli" when "Likes broccoli" is already applied
    # returns the conflicting trait_id if found, None if no conflict
    incoming_trait = get_trait_by_id(incoming_trait_id)

    # only white tier traits can conflict
    if incoming_trait is None or incoming_trait["tier"] != "white":
        return None

    # get the subject of the incoming trait e.g. "broccoli"
    incoming_subject = incoming_trait.get("subject")
    if incoming_subject is None:
        return None

    # check every trait already on the slate
    for existing_trait in slate["traits"]:
        existing_data = get_trait_by_id(existing_trait["trait_id"])
        if existing_data is None:
            continue

        # if same subject but different preference — that's a conflict
        if (existing_data.get("subject") == incoming_subject and
            existing_data.get("preference") != incoming_trait.get("preference")):
            return existing_trait["trait_id"]

    return None

def get_slate_traits_full(slate):
    # enriches a slate's trait list with full data from traits.json
    # replaces bare trait IDs with complete trait info including name and tier
    enriched_traits = []

    for slate_trait in slate["traits"]:
        trait_id = slate_trait["trait_id"]
        trait_data = get_trait_by_id(trait_id)

        if trait_data is None:
            print(f"Warning: trait {trait_id} not found in traits.json, skipping.")
            continue

        enriched_traits.append({
            "id":    trait_data["id"],
            "name":  trait_data["name"],
            "tier":  trait_data["tier"],
            "stars": slate_trait["stars"]
        })

    return enriched_traits