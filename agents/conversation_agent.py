import os
import re
from together import Together
from memory.memory_manager import MemoryManager

def detect_language(text: str) -> str:
    """
    Decide which dialect to use:
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
    def __init__(self,
                 model_name: str,
                 embed_model: str,
                 index_name: str):
        # LLM & Memory clients
        self.client = Together(api_key=os.getenv("TOGETHER_API_KEY"))
        self.model  = model_name
        self.mem    = MemoryManager(embed_model, index_name)

    def ask(self,
            session_id: str,
            user_message: str) -> str:
        # 1) Retrieve the top-3 past notes for this client
        past_notes = self.mem.retrieve(session_id, user_message, k=3)
        memory_block = "\n".join(past_notes) + "\n\n" if past_notes else ""

        # 2) Detect user’s language
        lang = detect_language(user_message)

        # 3) Choose a dialect-specific system prompt
        if lang == 'ar':
            sys_prompt = (
                "أنت El Consulto، الطبيب النفسي الافتراضي باللهجة المصرية العامية. "
                "في كل رد، امزج دفء القلب واحترافية الطب النفسي، مستخدمًا ما تعرفه عن المريض—"
                "تجاربه الماضية ومخاوفه وطموحاته—بدون ذكر عدد الجلسات أو أي عناوين. "
                "اجب بوضوح وباختصار، وقدّم خطوات بسيطة يمكن للمريض تطبيقها إذا رغب، "
                "ولا تطل في الكلام إذا لم يُطلب مزيد من الشرح."
            )
        elif lang == 'franco':
            sys_prompt = (
                "Enta El Consulto, el doctor ennafsy el AI el byetkallem Franco-Arab. "
                "Fe kol rad, estakhdem ton daafi w professional w weave fi ay details "
                "3arafna 3anha men el mareed—experiences, fears, ambitions—men gheir ma "
                "tsmaa el number beta3 el sessions. Rodd b jaww concise, w edee steps "
                "3amelya law el mareed 3ayez yelzem, bass matekthamsh ktir."
            )
        else:
            sys_prompt = (
                "You are El Consulto, an empathic psychiatrist AI. "
                "In each reply, combine a warm, professional tone with the specific details "
                "you know about this client’s journey—past challenges, fears, and hopes—"
                "without ever labeling sessions or using technical headings. "
                "Keep answers concise (1–3 sentences), offer a practical next step when helpful, "
                "and only expand if the patient asks for more detail."
            )

        # 4) Build the conversation
        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user",   "content": memory_block + user_message}
        ]

        # 5) Query the model
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens_to_sample=250,
            temperature=0.7,
        )
        answer = response.choices[0].message.content.strip()

        # 6) Save this turn in memory
        #    (stores user_message and AI answer for future context)
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
