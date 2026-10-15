# game_actions.py
# game rules as plain functions that return results (no input/print)
# the terminal menu and any future GUI both call these

from slate_manager import save_slate
from trait_manager import apply_trait_to_slate, get_conflicting_trait_id
from inventory_manager import remove_trait_from_inventory

def check_apply(slate, trait_id):
    # safe to call repeatedly (e.g. while hovering during a drag), changes nothing
    conflict_id = get_conflicting_trait_id(slate, trait_id)
    if conflict_id is not None:
        return {"ok": False, "reason": "conflict", "conflict_id": conflict_id}
    return {"ok": True}

def apply_from_inventory(player_id, slate, trait_id, stars):
    # the one place that applies an inventory trait to a slate
    check = check_apply(slate, trait_id)
    if not check["ok"]:
        return check  # nothing changed, inventory untouched

    apply_trait_to_slate(slate, trait_id, stars)
    save_slate(slate)
    remove_trait_from_inventory(player_id, trait_id, stars)
    return {"ok": True, "slate": slate}