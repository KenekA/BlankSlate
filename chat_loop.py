# chat_loop.py
# the main conversation loop for Blank Slate
# uses the prompt compiler to build the Slate's personality
# and maintains conversation history for context

import anthropic
from dotenv import load_dotenv
import os

# import our prompt compiler and slate data from prompt_compiler.py
from prompt_compiler import build_system_prompt
from slate_manager import get_active_slate

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# load the active slate from the save file
slate = get_active_slate()

if slate is None:
    print("No active slate found. Please set one in user_data.json.")
    exit()

# build the system prompt from the slate's traits
system_prompt = build_system_prompt(slate)

# stores the full conversation history
# grows with each message so Claude remembers context
conversation_history = []

print(f"Chatting with {slate['name']}. Type 'quit' to exit.\n")

while True:
    user_input = input("You: ")

    # skip empty inputs and restart the loop
    if user_input.strip() == "":
        print("Please enter a message.")
        continue

    # exit cleanly if user types quit
    if user_input.lower() == "quit":
        print("Goodbye!")
        break

    # add the user's message to the history
    conversation_history.append({
        "role": "user",
        "content": user_input
    })

    # send the full history and system prompt to Claude
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system=system_prompt,           # compiled personality from prompt_compiler.py
        messages=conversation_history   # full conversation history
    )

    # extract the text response
    assistant_reply = response.content[0].text

    # add Claude's reply to history so it remembers what it said
    conversation_history.append({
        "role": "assistant",
        "content": assistant_reply
    })

    print(f"\n{slate['name']}: {assistant_reply}\n")