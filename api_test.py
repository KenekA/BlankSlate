import anthropic
from dotenv import load_dotenv
import os

# load_dotenv() reads your .env file and makes your API key
# available to the rest of the script via os.getenv()
load_dotenv()

# create a client object — think of this as opening a connection
# to the Anthropic API using your key as identification
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# send a message to the API and store the response
response = client.messages.create(
    model="claude-haiku-4-5-20251001",  # which AI model to use (haiku = cheapest/fastest)
    max_tokens=1024,                     # maximum length of the response (1 token ≈ 1 word)

    # the system prompt is your Slate's personality instructions
    system="You are a shy and apologetic AI companion. You speak softly and always second-guess yourself.",

    # messages is the conversation history as a list
    messages=[
        {"role": "user", "content": "Hey, what's your name?"}
    ]
)

# the API returns a complex object — the actual text lives here:
# response.content is a list of content blocks
# [0] gets the first block
# .text gets the string text out of that block
print(response.content[0].text)