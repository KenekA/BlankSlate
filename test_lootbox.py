# test_lootbox.py
# tests the full lootbox open flow
# safe to delete once confirmed working

from lootbox_manager import open_lootbox
from inventory_manager import display_inventory

player_id = "player_001"

# open a few boxes and see what drops
print("Opening 5 starter boxes...\n")
for i in range(5):
    open_lootbox(player_id, "box_001")

# display the inventory after opening
display_inventory(player_id)
