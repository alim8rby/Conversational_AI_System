# -*- coding: utf-8 -*-
import os
import re
from together import Together, error as ta_errors
from memory.memory_manager import MemoryManager
from interview_manager import InterviewManager, SECTION_QUESTIONS

# Arabic translations of each structured‐interview question
AR_SECTION_QUESTIONS = {
    "personal_info":
        "لنفترض أن تبدأ بالتعريف عن نفسك: كم عمرك، وظيفتك، وظروف معيشتك، وما تريدني أن أعرفه عنك الآن؟",
    "chief_complaint":
        "ما هو السبب الرئيسي الذي دفعك للمجيء اليوم؟ بوصفك الخاص، ماذا ينتابك من قلق أكثر؟",
    "history_present_illness":
        "هل يمكنك أن تخبرني كيف تطورت هذه المشكلة مع مرور الوقت؟ متى بدأت، وكيف تغيرت، وهل لاحظت محفزات معينة؟",
    "past_psychiatric_history":
        "هل سبق وأن واجهت صعوبات نفسية مماثلة في الماضي أو تعاملت مع طبيب نفسي من قبل؟ شاركني أي تفاصيل عن ذلك.",
    "medical_history":
        "أخبرني عن تاريخك الطبي: أي حالات مزمنة، أدوية تتناولها، عمليات جراحية، أو علاجات مستمرة.",
    "surgical_history":
        "هل خضعت لأي عمليات جراحية تعتقد أنها مهمة بالنسبة لي أن أعرفها؟",
    "family_history":
        "هل هناك تاريخ مرضي أو نفسي في عائلتك؟ شارك ما تشعر بالراحة بالكشف عنه.",
    "substance_use_history":
        "هل استخدمت الكحول، التبغ، أو أي مواد مخدرة أو أدوية موصوفة؟ حدثني عن التكرار وأي مخاوف لديك.",
    "psychological_assessment":
        "أود أن أفهم شخصيتك وأسلوب تعاملِك: هل أجريت اختبارات مثل MBTI؟ إن لم تفعل، صف طرق تفكيرك ومشاعرك وسلوكك المعتادة.",
    "mental_state_exam":
        "كيف تصف مزاجك وأفكارك وحالتك الذهنية الآن؟ هل تشعر بالقلق، الهدوء، الحزن، الحماس، إلخ؟",
    "formulation":
        "بناءً على ما شاركت به، كيف تفسر سبب حدوث هذه الصعوبات؟ يمكنك التعبير بطريقتك الخاصة.",
    "provisional_diagnosis":
        "بناءً على كل ذلك، ما التسمية الأقرب لوصف تجربتك (مثل القلق، الاكتئاب، الوسواس، إلخ)؟ إذا لم تكن متأكدًا فهذا مقبول."
}

def detect_language(text: str) -> str:
    if re.search(r'[\u0600-\u06FF]', text):
        return 'ar'
    if re.search(r'\d', text):
        return 'franco'
    return 'en'

def is_valid_answer(text: str) -> bool:
    t = text.strip().lower()
    # reject pure laughter or single letters/too-short replies
    if re.fullmatch(r'(ha)+h?', t) or re.fullmatch(r'(heh)+', t) or len(t) <= 2:
        return False
    # require at least some substance
    return len(t) >= 10

class ConversationAgent:
    def __init__(self, model_name: str, embed_model: str, index_name: str):
        self.client   = Together(api_key=os.getenv("TOGETHER_API_KEY"))
        self.model    = model_name
        self.mem      = MemoryManager(embed_model, index_name)

        self.interviewer = InterviewManager()
        self.awaiting    = {}  # session_id -> last asked section
        self.histories   = {}  # session_id -> past turns

    def _clarify(self, session_id: str, last_sec: str, user_msg: str, lang: str) -> str:
        """Ask a focused clarifying question via the LLM."""
        last_q = (AR_SECTION_QUESTIONS if lang=='ar' else SECTION_QUESTIONS)[last_sec]
        # Build a minimal system prompt
        sys = (
            "You are a compassionate psychiatrist. When the client’s reply is unclear or too brief, "
            "express empathy and ask a clarifying follow-up about their last answer."
        )
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role":"system","content":sys},
                    {"role":"user",
                     "content":f"Last question: {last_q}\nUser answer: {user_msg}"}
                ],
                max_tokens_to_sample=150,
                temperature=0.7
            )
            return resp.choices[0].message.content.strip()
        except Exception:
            # fallback generic prompt
            if lang == 'ar':
                return "عذرًا، لم أفهم تمامًا. هل يمكنك توضيح أكثر؟"
            else:
                return "I’m sorry, I didn’t quite catch that—could you tell me more?"

    def ask(self, session_id: str, user_message: str) -> str:
        lang = detect_language(user_message)

        # 1) Handle non‐answers
        if not is_valid_answer(user_message):
            last_sec = self.awaiting.get(session_id)
            if last_sec:
                return self._clarify(session_id, last_sec, user_message, lang)
            # no section yet—generic empathic probe
            if lang == 'ar':
                return "أسمعك، لكني أريد أن أفهم أكثر. كيف تشعر بالضبط الآن؟"
            else:
                return "I hear you, but I’d like to understand better—how are you feeling right now?"

        # 2) Prepare session
        if session_id not in self.histories:
            self.histories[session_id] = []
        self.interviewer.init_session(session_id)

        # 3) Structured interview
        if not self.interviewer.is_complete(session_id):
            last_sec = self.awaiting.get(session_id)
            if last_sec:
                self.interviewer.record_response(session_id, user_message)

            next_sec = self.interviewer.next_section(session_id)
            # pick question in correct language
            if lang == 'ar':
                question = AR_SECTION_QUESTIONS[next_sec]
                greet = "مرحبًا! أنا El Consulto، طبيبك النفسي الافتراضي."
                thanks = "شكرًا لمشاركتك."
            else:
                question = SECTION_QUESTIONS[next_sec]
                greet = "Hello! I’m El Consulto, your virtual psychiatrist."
                thanks = "Thank you for sharing."

            prompt = (greet + " " + question) if last_sec is None else (thanks + " " + question)
            self.awaiting[session_id] = next_sec
            return prompt

        # 4) Free‐form therapy
        sheet = self.interviewer.get_sheet(session_id)
        sheet_text = "\n".join(f"{k.replace('_',' ').title()}: {v}"
                               for k,v in sheet.items())
        mem_notes = self.mem.retrieve(session_id, user_message, k=3)
        memory_block = ("\n".join(mem_notes) + "\n\n") if mem_notes else ""

        # system prompt per language
        if lang == 'ar':
            sys = (
                "أنت El Consulto، المعالج النفسي الودود. استخدم ورقة المعلومات المقدمة "
                "لتقديم ردود موجزة وعملية. إذا ابتعد المريض عن الموضوع، أعده بلطف إلى مشاعره."
            )
            error = "عذرًا، حدث خطأ. هل يمكنك المحاولة مرة أخرى؟"
        else:
            sys = (
                "You are El Consulto, the friendly psychiatrist AI. Use the provided "
                "patient sheet to craft concise, actionable responses. If the user drifts off-topic, gently guide them back to their feelings."
            )
            error = "Sorry, something went wrong. Could you try again?"

        # assemble messages
        msgs = [
            {"role":"system","content":sys},
            {"role":"system","content":"Patient Sheet:\n"+sheet_text}
        ]
        msgs.extend(self.histories[session_id])
        msgs.append({"role":"user","content":memory_block+user_message})

        # call LLM
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=msgs,
                max_tokens_to_sample=250,
                temperature=0.7,
            )
            answer = resp.choices[0].message.content.strip()
        except Exception:
            return error

        # record history & memory
        self.histories[session_id].append({"role":"user",    "content":user_message})
        self.histories[session_id].append({"role":"assistant","content":answer})
        self.mem.add(session_id, user_message, answer)

        return answer

if __name__ == "__main__":
    agent = ConversationAgent(
        model_name="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        embed_model="togethercomputer/m2-bert-80M-8k-retrieval",
        index_name="wss-ai-memory"
    )
    # test flows
    for inp in ["hahaha", "k", "أنا مش عارف أنام من قلقي بشأن شغلي"]:
        print("User:", inp)
        print("Bot :", agent.ask("demo", inp))
        print("---")
