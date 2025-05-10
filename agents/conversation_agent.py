# -*- coding: utf-8 -*-
import os
import re
import math
from together import Together, error as ta_errors
from memory.memory_manager import MemoryManager
from interview_manager import InterviewManager, SECTION_QUESTIONS

# Egyptian‐Arabic versions of the structured questions
AR_SECTION_QUESTIONS = {
    "personal_info":          "لنفترض أن تبدأ بالتعريف عن نفسك: كم عمرك، وظيفتك، وظروف معيشتك؟",
    "chief_complaint":        "ما هو السبب الرئيسي الذي دفعك للمجيء اليوم؟ بوصفك الخاص، ماذا يقلقك أكثر؟",
    "history_present_illness":"هل يمكنك أن تخبرني كيف تطورت هذه المشكلة مع مرور الوقت؟ متى بدأت وكيف تغيرت؟",
    "past_psychiatric_history":"هل سبق لك التعامل مع طبيب نفسي أو مررت بصعوبات مماثلة من قبل؟ شاركني التفاصيل.",
    "medical_history":        "أخبرني عن تاريخك الطبي: أمراض مزمنة، أدوية تتناولها، أو جراحات خضعتها لها.",
    "surgical_history":       "هل أجريت أي عمليات جراحية مهمة يجب أن أعرفها؟",
    "family_history":         "هل هناك تاريخ مرضي أو نفسي في عائلتك؟ قلت لي عنه ما تشعر بالراحة بمشاركته.",
    "substance_use_history":  "هل استخدمت الكحول أو التبغ أو أي مواد أخرى؟ حدثني عن الكم والمدة.",
    "psychological_assessment":"أريد فهم شخصيتك: إن لم تأخذ اختبارات مثل MBTI، صف طريقتك في التفكير والشعور.",
    "mental_state_exam":      "كيف تصف مزاجك وأفكارك الآن؟ هل تشعر بالقلق، الهدوء، الحزن، إلخ؟",
    "formulation":            "بناءً على ما شاركت به، كيف تفسر سبب هذه الصعوبات؟",
    "provisional_diagnosis":  "ما التسمية الأقرب لوصف تجربتك (قلق، اكتئاب، إلخ)؟ إن لم تكن متأكدًا فلا بأس."
}

def detect_language(text: str) -> str:
    if re.search(r'[\u0600-\u06FF]', text):
        return 'ar'
    if re.search(r'\d', text):
        return 'franco'
    return 'en'

def is_valid_answer(text: str) -> bool:
    t = text.strip().lower()
    if re.fullmatch(r'(ha)+h?', t) or re.fullmatch(r'(heh)+', t) or len(t) <= 2:
        return False
    return len(t) >= 10

class ConversationAgent:
    def __init__(self, model_name: str, embed_model: str, index_name: str):
        # LLM & RAG
        self.client   = Together(api_key=os.getenv("TOGETHER_API_KEY"))
        self.model    = model_name
        self.mem      = MemoryManager(embed_model, index_name)

        # Structured interview state
        self.interviewer   = InterviewManager()
        self.awaiting      = {}  # session_id -> last section
        self.histories     = {}  # session_id -> chat history
        self.clarify_counts= {}  # session_id -> {section: count}

    def _semantic_similarity(self, q: str, a: str) -> float:
        """Compute cosine similarity between embeddings of q and a."""
        try:
            resp = self.mem.client.embeddings.create(
                model=self.mem.embed_model,
                input=[q, a]
            )
            vq = resp.data[0].embedding
            va = resp.data[1].embedding
        except Exception:
            return 1.0
        dot = sum(x*y for x,y in zip(vq, va))
        mag_q = math.sqrt(sum(x*x for x in vq))
        mag_a = math.sqrt(sum(x*x for x in va))
        return dot / (mag_q * mag_a) if mag_q and mag_a else 0.0

    def _classify_answer(self, q: str, a: str) -> bool:
        """Ask the LLM if 'a' addresses question 'q'; return True for Yes."""
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role":"system",
                     "content":"You are a psychiatrist. Does the following answer respond to the question? Reply exactly 'Yes' or 'No'."},
                    {"role":"user",
                     "content":f"Question: {q}\nAnswer: {a}"}
                ],
                max_tokens_to_sample=3,
                temperature=0
            )
            ans = resp.choices[0].message.content.strip().lower()
            return ans.startswith('yes')
        except Exception:
            return True

    def _tiered_clarifier(self, session_id: str, section: str, lang: str) -> str:
        """Return a Level-1, 2, or 3 clarifying prompt, escalating with each call."""
        # Initialize counters
        counts = self.clarify_counts.setdefault(session_id, {})
        c = counts.get(section, 0)

        # Gather up to two past facts for Level 3
        sheet = self.interviewer.get_sheet(session_id)
        facts = [v for v in sheet.values() if v]
        fact1 = facts[0] if len(facts)>0 else ""
        fact2 = facts[1] if len(facts)>1 else ""

        # Define three levels
        if lang == 'ar':
            levels = [
                "عذرًا، لم أفهم تمامًا. هل يمكنك التوضيح أكثر؟",
                "أحيانًا تظهر المشاعر في الجسد—ماذا تشعر فيه جسديًا الآن؟",
                f"ذكرت سابقًا أنك {fact1} و{fact2}. كيف يرتبط تعليقك بهذا؟"
            ]
        elif lang == 'franco':
            levels = [
                "M3lesh, mafehemtsh kwayes—momken toz7 aktar?",
                "Ba3den el mash3oor betban fe el badan—enta 7asas ezzay delwa2ty?",
                f"Enta 2olt abl keda en {fact1} w {fact2}. Ezay elly enta 2olto mertaabet keda?"
            ]
        else:
            levels = [
                "I’m sorry, I didn’t quite catch that. Could you tell me more?",
                "Sometimes feelings show up in our body—what do you notice physically right now?",
                f"You mentioned earlier that \"{fact1}\" and \"{fact2}\"—how does that relate to your answer?"
            ]

        # Cap at Level 3
        prompt = levels[min(c, 2)]
        counts[section] = c + 1
        return prompt

    def ask(self, session_id: str, user_message: str) -> str:
        lang = detect_language(user_message)

        # 1) NON‐ANSWER CHECK → Clarify
        if not is_valid_answer(user_message):
            last = self.awaiting.get(session_id)
            if last:
                return self._tiered_clarifier(session_id, last, lang)
            # no last question yet
            if lang == 'ar':
                return "أسمعك، لكني أريد أن أفهم أكثر. كيف تشعر بالضبط الآن؟"
            elif lang == 'franco':
                return "I hear you, but I’d like to understand better—how are you feeling right now?"
            else:
                return "I hear you, but I’d like to understand better—how are you feeling right now?"

        # 2) SESSION INIT
        self.interviewer.init_session(session_id)
        self.histories.setdefault(session_id, [])

        # 3) STRUCTURED INTERVIEW PHASE
        if not self.interviewer.is_complete(session_id):
            last = self.awaiting.get(session_id)
            # If we have a last question, check relevance
            if last:
                # pick correct language question text
                q_text = (AR_SECTION_QUESTIONS if lang=='ar' else SECTION_QUESTIONS)[last]
                sim = self._semantic_similarity(q_text, user_message)
                if sim < 0.4 or not self._classify_answer(q_text, user_message):
                    return self._tiered_clarifier(session_id, last, lang)
                # record valid answer
                self.interviewer.record_response(session_id, user_message)
                # reset clarifier count
                self.clarify_counts.get(session_id, {}).pop(last, None)

            # Ask the next section
            nxt = self.interviewer.next_section(session_id)
            q    = (AR_SECTION_QUESTIONS if lang=='ar' else SECTION_QUESTIONS)[nxt]
            if lang == 'ar':
                prompt = ("مرحبًا! أنا El Consulto، طبيبك النفسي الافتراضي. " if last is None else "شكرًا لمشاركتك. ") + q
            elif lang == 'franco':
                prompt = ("Hey! Ana El Consulto, el doctor ennafsy beta3ak. " if last is None else "Shokran 3ala el mosharaka. ") + q
            else:
                prompt = ("Hello! I’m El Consulto, your virtual psychiatrist. " if last is None else "Thank you for sharing. ") + q

            self.awaiting[session_id] = nxt
            return prompt

        # 4) FREE‐FORM THERAPY PHASE
        sheet = self.interviewer.get_sheet(session_id)
        sheet_text = "\n".join(f"{k.replace('_',' ').title()}: {v}"
                               for k,v in sheet.items())
        notes = self.mem.retrieve(session_id, user_message, k=3)
        mem_block = ("\n".join(notes) + "\n\n") if notes else ""

        if lang == 'ar':
            sys = ("أنت El Consulto، المعالج الودود. استخدم ورقة المعلومات "
                   "لتقديم ردود موجزة وعملية. إذا ابتعد المريض، أعده بلطف.")
            err = "عذرًا، حدث خطأ. هل يمكنك المحاولة مرة أخرى؟"
        elif lang == 'franco':
            sys = ("You are El Consulto, the friendly psychiatrist AI. Use the sheet "
                   "to craft concise, actionable responses. If the user drifts, gently refocus.")
            err = "M3lesh, fe moshkela. 7awel tani law sama7t."
        else:
            sys = ("You are El Consulto, an empathic psychiatrist AI. Use the provided sheet "
                   "to give concise, actionable responses. If the user drifts off-topic, gently bring them back.")
            err = "Sorry, something went wrong. Could you try again?"

        msgs = [
            {"role":"system","content":sys},
            {"role":"system","content":"Patient Sheet:\n"+sheet_text}
        ]
        msgs.extend(self.histories[session_id])
        msgs.append({"role":"user","content":mem_block + user_message})

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=msgs,
                max_tokens_to_sample=250,
                temperature=0.7,
            )
            answer = resp.choices[0].message.content.strip()
        except Exception:
            return err

        # record & persist
        self.histories[session_id].append({"role":"user",    "content":user_message})
        self.histories[session_id].append({"role":"assistant","content":answer})
        self.mem.add(session_id, user_message, answer)

        return answer


if __name__ == "__main__":
    a = ConversationAgent(
        model_name="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        embed_model="togethercomputer/m2-bert-80M-8k-retrieval",
        index_name="wss-ai-memory"
    )
    for inp in ["hahaha", "k", "I feel stuck at work", "مش فاهم حاجة"]:
        print("User:", inp)
        print("Bot :", a.ask("demo", inp))
        print("---")
