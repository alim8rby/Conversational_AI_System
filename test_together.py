import os
from together import Together

# Initialize the client
client = Together(api_key=os.getenv("TOGETHER_API_KEY"))

# Send a single user message
resp = client.chat.completions.create(
    model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    messages=[{"role": "user", "content": "Hello, world!"}],
)

# Print the reply
print("Together says:", resp.choices[0].message.content)
