import openai

class ConversationAgent:
    def __init__(self, model_name: str, api_key: str):
        openai.api_key = api_key
        self.model = model_name

    def ask(self, prompt: str) -> str:
        resp = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return resp.choices[0].message.content

if __name__ == "__main__":
    agent = ConversationAgent(
        model_name="ada:ft-your-org:wss-test-xxxx",
        api_key="sk-..."
    )
    print(agent.ask("Patient: I feel lost."))
