# memory_manager.py
# handles persistent chat memory for each slate
# full history is saved to disk, but only a recent window is sent to Claude
# one memory file per player per slate: players/<player_id>/memory/<slate>.json

import json
import os

PLAYERS_FOLDER = "players"

# how many recent messages get sent to Claude on each turn
# (a user message + a reply = 2 messages, so 30 = about 15 exchanges)
MAX_WINDOW = 30


def get_memory_path(player_id, slate_name):
    # builds the file path to a slate's memory file
    # slate name is lowercased to match how slate_manager names its files
    return os.path.join(PLAYERS_FOLDER, player_id, "memory", f"{slate_name.lower()}.json")


def load_memory(player_id, slate_name):
    # loads a slate's memory from disk, or returns a fresh empty one
    # "summary" is reserved for the rolling summary step (not used yet)
    path = get_memory_path(player_id, slate_name)
    if not os.path.exists(path):
        return {"slate": slate_name, "summary": "", "messages": []}
    with open(path, "r") as f:
        return json.load(f)


def save_memory(player_id, slate_name, memory):
    # saves memory safely: write to a temp file first, then swap it in
    # if the program crashes mid-write, the old file stays intact
    path = get_memory_path(player_id, slate_name)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    temp_path = path + ".tmp"
    with open(temp_path, "w") as f:
        json.dump(memory, f, indent=4)
    os.replace(temp_path, path)


def add_exchange(memory, user_text, assistant_text):
    # records one full exchange (the user's message and the reply) together
    # call this only AFTER the API call succeeds, so a failed call
    # never leaves a dangling user message in the saved history
    memory["messages"].append({"role": "user", "content": user_text})
    memory["messages"].append({"role": "assistant", "content": assistant_text})


def get_recent_messages(memory, limit=MAX_WINDOW):
    # returns the last `limit` messages to send to Claude
    # the full history stays on disk, only this slice goes over the API
    recent = memory["messages"][-limit:]

    # the API expects the conversation to start with a user message,
    # so if the cut landed on an assistant reply, drop it
    while recent and recent[0]["role"] != "user":
        recent = recent[1:]

    return recent


def clear_memory(player_id, slate_name):
    # wipes a slate's saved conversation (e.g. a "forget everything" option)
    path = get_memory_path(player_id, slate_name)
    if os.path.exists(path):
        os.remove(path)
