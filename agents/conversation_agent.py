import os
import re
from together import Together
from memory.memory_manager import MemoryManager

def detect_language(text: str) -> str:
    """
    Rudimentary language detection:
    - Arabic letters → 'ar'
    - Digits (e.g. '3andy') → 'franco'
    - Otherwise → 'en'
    """
    if re.search(r'[\u0600-\u06FF]', text):
        return 'ar'
    if re.search(r'\d', text):
        return 'franco'
    return 'en'

class ConversationAgent:
    def __init__(self, model_name: str, embed_model: str, index_name: str):
        # Initialize LLM client
        self.client = Together(api_key=os.getenv("TOGETHER_API_KEY"))
        self.model  = model_name
        # Initialize session‐scoped memory
        self.mem = MemoryManager(embed_model, index_name)

    def ask(self, session_id: str, user_message: str) -> str:
        # 1) Retrieve this session’s past keys
        keys = self.mem.retrieve(session_id, user_message, k=3)
        context = f"Context: {'; '.join(keys)}\n\n" if keys else ""

        # 2) Auto-detect language
        lang = detect_language(user_message)

        # 3) Build a more nuanced system prompt per language
        if lang == 'ar':
            sys_prompt = (
                "أنت El Consulto، الطبيب النفسي الافتراضي، وتقدم دعمًا شخصيًا "
                "مبنيًا على رحلات كل مريض الفريدة. عندما تتلقى رسالة من المريض، "
                "امزج ما لديك من ذكريات عن سياقه (المذكورة في الـ Context) مع "
                "حساسيتك للغة والثقافة المصرية العامية، واستجب بدفء ورحمة، "
                "مُظهِرًا تفهمًا عميقًا لقصته وتجاربه. لا تطلب من المريض أن يجيب "
                "أنت فقط أجب كالمعالج—بأسلوب لبق ومهني."
            )
        elif lang == 'franco':
            sys_prompt = (
                "Enta El Consulto, el doctor ennafsy el AI el byetkallem Franco-Arab. "
                "Enta tedee da3m shakhsiyy welaih, betistakhdem Context el session "
                "3ashan tifham history el mareed. Rodd b tone daafi w mohandez, "
                "you weave specific session notes into your reply, making each "
                "response feel tailored to their story. Maa tdawrsh el mareed "
                "yerd 3ala nafsu—enta enta el therapist."
            )
        else:
            sys_prompt = (
                "You are El Consulto’s empathic psychiatrist AI. You offer warm, "
                "personalized support by weaving each client’s unique journey—"
                "including their prior session notes (provided in Context)—into "
                "every therapeutic response. Adapt your tone to be compassionate, "
                "culturally sensitive, and entirely focused on the patient’s "
                "needs. Never ask the patient to respond to themselves; always "
                "reply as the therapist with clarity, respect, and genuine care."
            )

        # 4) Build and send the chat
        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user",   "content": context + user_message}
        ]
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens_to_sample=300,
            temperature=0.7,
        )
        answer = resp.choices[0].message.content

        # 5) Save this exchange in memory
        self.mem.add(session_id, user_message, answer)
        return answer

if __name__ == "__main__":
    # Quick manual test
    agent = ConversationAgent(
        model_name="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        embed_model="togethercomputer/m2-bert-80M-8k-retrieval",
        index_name="wss-ai-memory"
    )
    print(agent.ask("test-session", "I have an existential crisis"))
