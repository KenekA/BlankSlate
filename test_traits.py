# test_traits.py
# tests the trait combining logic and prompt generation
# safe to delete once confirmed working

import slate_manager
import trait_manager
from prompt_compiler import build_system_prompt

slate_manager.initialize()

# load luna from the save file
luna = slate_manager.load_slate("luna")
print("Loaded slate:", luna["name"])

# test combining — apply a trait luna already has
print("\n--- Testing trait combine ---")
luna = trait_manager.apply_trait_to_slate(luna, "red_003", 3)  # luna has 5 stars, adding 3 more = capped at 10? no, 8

# test adding a brand new trait
print("\n--- Testing new trait ---")
luna = trait_manager.apply_trait_to_slate(luna, "blue_001", 7)

# test the star cap
print("\n--- Testing star cap ---")
luna = trait_manager.apply_trait_to_slate(luna, "red_003", 9)  # already at 8, adding 9 should cap at 10

# save the updated slate
slate_manager.save_slate(luna)

# print the full generated prompt
print("\n--- Generated system prompt ---")
print(build_system_prompt(luna))