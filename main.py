# main.py
# the main entry point for Blank Slate
# ties all systems together into a single interactive menu
# this will eventually be replaced by a proper GUI

import os
from dotenv import load_dotenv
import anthropic
from trait_manager import apply_trait_to_slate, get_trait_by_id, get_conflicting_trait_id
from memory_manager import load_memory, save_memory, add_exchange, get_recent_messages
from game_actions import apply_from_inventory

from slate_manager import (
    initialize,           # sets up folders and files on first run
    get_active_slate,     # loads the currently active slate
    get_all_slates,       # lists all slates in the collection
    set_active_slate,     # changes the active slate
    save_slate            # saves a slate to disk
)
from prompt_compiler import build_system_prompt
from trait_manager import apply_trait_to_slate, get_trait_by_id
from inventory_manager import (
    create_player,
    load_inventory,       # loads the player's inventory
    display_inventory,    # prints a readable inventory summary
    remove_trait_from_inventory  # removes a trait copy from inventory
)
from lootbox_manager import open_lootbox, load_lootboxes

load_dotenv()



# the player ID for now — will come from a login system later
PLAYER_ID = "player_001"

# create the anthropic client once at the top level
# so all parts of the app can use the same connection
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def chat_with_slate():
    # loads the active slate, compiles its personality,
    # restores its saved memory, and starts a conversation loop with Claude
    slate = get_active_slate()
    if slate is None:
        print("No active slate. Please select one first.")
        return

    system_prompt = build_system_prompt(slate)
    memory = load_memory(PLAYER_ID, slate["name"])

    print(f"\nNow chatting with {slate['name']}. Type 'quit' to return to menu.")
    if memory["messages"]:
        print(f"({slate['name']} remembers your earlier conversations.)\n")
    else:
        print()

    while True:
        user_input = input("You: ")

        if user_input.lower() == "quit":
            print(f"Leaving chat with {slate['name']}.\n")
            break

        if user_input.strip() == "":
            print("Please enter a message.")
            continue

        # recent saved messages plus the new one (not saved yet)
        messages = get_recent_messages(memory) + [
            {"role": "user", "content": user_input}
        ]

        try:
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1024,
                system=system_prompt,
                messages=messages
            )
        except anthropic.APIError as e:
            # nothing was saved, so the chat history stays clean
            print(f"\n[Couldn't reach {slate['name']}: {e}]\n")
            continue

        assistant_reply = response.content[0].text

        # save the exchange only after the API call succeeded
        add_exchange(memory, user_input, assistant_reply)
        save_memory(PLAYER_ID, slate["name"], memory)

        print(f"\n{slate['name']}: {assistant_reply}\n")

def open_lootbox_menu():
    # shows available lootboxes and lets the player open one
    lootboxes = load_lootboxes()

    print("\n--- Available lootboxes ---")
    for box_id, box in lootboxes.items():
        print(f"  [{box_id}] {box['name']} — {box['cost']} coins — {box['description']}")

    print("\nEnter a box ID to open it, or 'back' to return.")
    choice = input("> ").strip()

    if choice.lower() == "back":
        return

    if choice not in lootboxes:
        print("Invalid box ID.")
        return

    # open the box and show the result
    result = open_lootbox(PLAYER_ID, choice)
    if result:
        print(f"\n  Tier:  {result['tier'].upper()}")
        print(f"  Trait: {result['trait_id']}")
        print(f"  Stars: {result['stars']}/10")

def inventory_menu():
    # shows the player's inventory and lets them apply a trait to their slate
    display_inventory(PLAYER_ID)

    inventory = load_inventory(PLAYER_ID)
    if not inventory:
        return

    print("Enter a trait ID to apply it to your active Slate, or 'back' to return.")
    trait_id = input("> ").strip()

    if trait_id.lower() == "back":
        return

    if trait_id not in inventory:
        print("Trait not found in inventory.")
        return

    # show available copies and their star ratings
    copies = inventory[trait_id]["copies"]
    print(f"\nAvailable copies of {trait_id}:")
    for i, copy in enumerate(copies):
        print(f"  [{i}] {copy['stars']} stars")

    print("Enter the number of the copy to apply:")
    try:
        # try to convert the input to an integer
        # if the player types something that isn't a number this will fail
        index = int(input("> ").strip())
        if index < 0 or index >= len(copies):
            print("Invalid selection.")
            return
    except ValueError:
        # catches the case where input() cant be converted to int
        print("Please enter a number.")
        return

    stars = copies[index]["stars"]

    # load the active slate, apply the trait, save it back
    slate = get_active_slate()
    if slate is None:
        print("No active slate.")
        return

    # get the full trait data so we can show the name
    trait_data = get_trait_by_id(trait_id)
    trait_name = trait_data["name"] if trait_data else trait_id

    result = apply_from_inventory(PLAYER_ID, slate, trait_id, stars)
    if not result["ok"]:
        conflict_data = get_trait_by_id(result["conflict_id"])
        conflict_name = conflict_data["name"] if conflict_data else result["conflict_id"]
        print(f"\nCan't apply {trait_name}: {slate['name']} already has {conflict_name}.")
        print("Nothing was used. The trait is still in your inventory.")
        return

    print(f"\nApplied {trait_name} ({stars} stars) to {slate['name']}!")

    # apply the trait and save
    slate = apply_trait_to_slate(slate, trait_id, stars)
    save_slate(slate)

    # remove the used copy from inventory
    remove_trait_from_inventory(PLAYER_ID, trait_id, stars)

    print(f"\nApplied {trait_name} ({stars} stars) to {slate['name']}!")

def slate_menu():
    # shows the player's slate collection and lets them switch active slate
    slates = get_all_slates()

    print("\n--- Your slate collection ---")
    for name in slates:
        print(f"  {name}")

    print("\nEnter a slate name to make it active, or 'back' to return.")
    choice = input("> ").strip()

    if choice.lower() == "back":
        return

    if choice.lower() not in [s.lower() for s in slates]:
        print("Slate not found.")
        return

    set_active_slate(choice)

def main():
    # runs once at startup to make sure all folders and files exist
        # runs once at startup to make sure all folders and files exist
    initialize()
    create_player(PLAYER_ID)

    print("Welcome to Blank Slate.")

    while True:
        # show the active slate name in the menu header
        slate = get_active_slate()
        slate_name = slate["name"] if slate else "None"

        print(f"\n--- Main Menu --- (Active Slate: {slate_name})")
        print("  [1] Chat with your Slate")
        print("  [2] Open a lootbox")
        print("  [3] View inventory")
        print("  [4] Switch active Slate")
        print("  [5] Quit")

        choice = input("\n> ").strip()

        if choice == "1":
            chat_with_slate()
        elif choice == "2":
            open_lootbox_menu()
        elif choice == "3":
            inventory_menu()
        elif choice == "4":
            slate_menu()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, please enter 1-5.")

# this block ensures main() only runs when you execute this file directly
# and not when another file imports from it
if __name__ == "__main__":
    main()