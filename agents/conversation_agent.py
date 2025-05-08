import os
import re
from together import Together
from memory.memory_manager import MemoryManager

def detect_language(text: str) -> str:
    """
    - Arabic letters → 'ar'
    - Digits (e.g. '3andi', '7elwa') → 'franco'
    - Otherwise → 'en'
    """
    if re.search(r'[\u0600-\u06FF]', text):
        return 'ar'
    if re.search(r'\d', text):
        return 'franco'
    return 'en'

class ConversationAgent:
    def __init__(self, model_name: str, embed_model: str, index_name: str):
        # LLM client
        self.client = Together(api_key=os.getenv("TOGETHER_API_KEY"))
        self.model  = model_name
        # Session‐scoped memory
        self.mem    = MemoryManager(embed_model, index_name)

    def ask(self, session_id: str, user_message: str) -> str:
        # 1) Retrieve relevant memories for this session
        keys = self.mem.retrieve(session_id, user_message, k=3)

        # 2) Auto‐detect language
        lang = detect_language(user_message)

        # 3) Rich, adaptive system prompt
        if lang == 'ar':
            sys_prompt = (
                "أنت El Consulto، الطبيب النفسي الافتراضي باللهجة المصرية العامية. "
                "في ردودك، امزج الأسلوب الدافئ والمهني مع "
                "تفاصيل ما عرفته عن المريض في هذه الجلسة—"
                "تجاربهم، مخاوفهم، وتطلعاتهم—دون الإشارة إلى عدد الجلسات أو التسميات. "
                "استجب بدفء وتفهّم عميق، وقدم خطوات عملية أو تأملية تناسب سياقهم."
            )
        elif lang == 'franco':
            sys_prompt = (
                "Enta El Consulto, el doctor ennafsy el AI el byetkallem Franco-Arab. "
                "Weave fi ton daafi w professional, estakhdem ay tafaseel 3arafna 3anha "
                "men el session—experiences, fears, goals—men gheir ma tetozer el session number. "
                "Oddee derseyya amali w kalam ya3mel impact 3ala el mareed."
            )
        else:
            sys_prompt = (
                "You are El Consulto’s empathic psychiatrist AI. "
                "In every reply, combine a warm, professional tone with the specific details "
                "you know about this client from their previous sessions—"
                "their experiences, concerns, and goals—"
                "without ever mentioning session counts or labels. "
                "Offer insights and gentle guidance tailored to their unique journey."
            )

        # 4) Build messages
        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user",   "content": user_message}
        ]

        # 5) Query the model
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens_to_sample=300,
            temperature=0.7,
        )
        answer = resp.choices[0].message.content

        # 6) Save this exchange in memory
        self.mem.add(session_id, user_message, answer)
        return answer

if __name__ == "__main__":
    # Quick manual test (English)
    agent = ConversationAgent(
        model_name="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        embed_model="togethercomputer/m2-bert-80M-8k-retrieval",
        index_name="wss-ai-memory"
    )
    print(agent.ask("test-session", "I have an existential crisis"))
