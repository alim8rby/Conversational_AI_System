import os
from together import Together

class ConversationAgent:
    def __init__(self, model_name: str):
        self.client = Together(api_key=os.getenv("TOGETHER_API_KEY"))
        self.model = model_name

    def ask(self, user_message: str) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": user_message}],
            max_tokens_to_sample=300,
            temperature=0.7,
        )
        return resp.choices[0].message.content

if __name__ == "__main__":
    agent = ConversationAgent("meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")
    print(agent.ask("Patient: I feel lost."))
