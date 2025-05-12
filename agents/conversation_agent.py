# -*- coding: utf-8 -*-
import os
import re
import math
from together import Together, error as ta_errors
from memory.memory_manager import MemoryManager
from interview_manager import InterviewManager, SECTION_QUESTIONS

# Egyptian‐Arabic versions of the structured questions
AR_SECTION_QUESTIONS = {
    "personal_info":           "لنفترض أنك تبدأ بالتعريف عن نفسك: كم عمرك، وظيفتك، وظروف معيشتك؟",
    "chief_complaint":         "ما هو السبب الرئيسي لقدومك اليوم؟ بوصفك الخاص، ماذا يقلقك أكثر؟",
    "history_present_illness": "هل تستطيع أن تخبرني كيف تطورت هذه المشكلة مع مرور الوقت؟ متى بدأت؟",
    "past_psychiatric_history":"هل سبق أن تعاملت مع طبيب نفسي أو مررت بصعوبات مماثلة من قبل؟ شاركني التفاصيل.",
    "medical_history":         "أخبرني عن تاريخك الطبي: أمراض مزمنة، أدوية، جراحات، أو علاجات مستمرة.",
    "surgical_history":        "هل خضعت لأي عملية جراحية تعتقد أنها مهمة بالنسبة لي أن أعرفها؟",
    "family_history":          "هل هناك تاريخ مرضي أو نفسي في عائلتك؟ شارك ما تشعر بالارتياح للكشف عنه.",
    "substance_use_history":   "هل استخدمت الكحول، التبغ، أو أي مواد مخدرة؟ حدثني عن التكرار وأي مخاوف.",
    "psychological_assessment":(
        "أريد أن أفهم شخصيتك: إن لم تأخذ اختبارات مثل MBTI، صف طريقتك في التفكير والشعور."
    ),
    "mental_state_exam":       "كيف تصف مزاجك وأفكارك وحالتك الذهنية الآن؟",
    "formulation":             "بناءً على ما شاركت به، كيف تفسر سبب هذه الصعوبات؟",
    "provisional_diagnosis":   "ما التسمية الأقرب لوصف تجربتك (قلق، اكتئاب، إلخ)؟ إن لم تكن متأكدًا فلا بأس."
}

def detect_language(text: str) -> str:
    if re.search(r'[\u0600-\u06FF]', text):
        return 'ar'
    if re.search(r'\d', text):
        return 'franco'
    return 'en'

def is_valid_answer(text: str) -> bool:
    t = text.strip().lower()
    # reject pure laughter or single letters or too‐short replies
    if re.fullmatch(r'(ha)+h?', t) or re.fullmatch(r'(heh)+', t) or len(t) <= 2:
        return False
    return len(t) >= 10

class ConversationAgent:
    def __init__(self,
                 model_name: str,
                 embed_model: str,
                 index_name: str):
        # LLM and RAG memory
        self.client   = Together(api_key=os.getenv("TOGETHER_API_KEY"))
        self.model    = model_name
        self.mem      = MemoryManager(embed_model, index_name)

        # Structured interview
        self.interviewer    = InterviewManager()
        self.awaiting       = {}  # session_id -> last section asked
        self.histories      = {}  # session_id -> message history
        self.clarify_counts = {}  # session_id -> {section: count}

    def _semantic_similarity(self, q: str, a: str) -> float:
        """Compute cosine similarity between embeddings of q and a via Together embeddings."""
        try:
            r = self.client.embeddings.create(
                model=self.mem.embed_model,
                input=[q, a]
            )
            vq, va = r.data[0].embedding, r.data[1].embedding
            dot = sum(x*y for x,y in zip(vq, va))
            mq = math.sqrt(sum(x*x for x in vq))
            ma = math.sqrt(sum(x*x for x in va))
            return dot / (mq * ma) if mq and ma else 0.0
        except Exception:
            # treat embed errors as zero similarity
            return 0.0

    def _classify_answer(self, q: str, a: str, lang: str) -> bool:
        """Use the LLM to ask Yes/No if answer a addresses question q, localized."""
        if lang == 'ar':
            sys = "أنت طبيب نفسي. هل تجيب هذه الإجابة على السؤال؟ أجب بـنعم أو لا."
        else:
            sys = "You are a psychiatrist. Does this answer address the question? Reply exactly 'Yes' or 'No'."

        try:
            r = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role":"system", "content": sys},
                    {"role":"user",   "content": f"Question: {q}\nAnswer: {a}"}
                ],
                max_tokens_to_sample=3,
                temperature=0.0
            )
            ans = r.choices[0].message.content.strip().lower()
            return ans.startswith('yes') or ans.startswith('نعم')
        except Exception:
            return False

    def _tiered_clarifier(self, session_id: str, section: str, lang: str) -> str:
        """
        Return a clarifying question:
         - Level 1: Simple empathy
         - Level 2: Body‐aware probe
         - Level 3: Contextual re‐raising (only if ≥2 facts recorded)
        """
        counts = self.clarify_counts.setdefault(session_id, {})
        c      = counts.get(section, 0)

        # gather up to two recorded facts
        sheet = self.interviewer.get_sheet(session_id)
        facts = [v for v in sheet.values() if v]
        fact1 = facts[0] if len(facts)>0 else ""
        fact2 = facts[1] if len(facts)>1 else ""

        # define levels
        if lang == 'ar':
            levels = [
                "عذرًا، لم أفهم تمامًا. هل يمكنك التوضيح أكثر؟",
                "أحيانًا تظهر المشاعر في الجسد—ماذا تشعر فيه جسديًا الآن؟",
                f"ذكرت سابقًا أنك {fact1} و{fact2}. كيف يرتبط ذلك بردك؟"
            ]
        else:
            levels = [
                "I’m sorry, I didn’t quite catch that. Could you tell me more?",
                "Sometimes feelings show up in our body—what do you notice physically right now?",
                f"You mentioned earlier \"{fact1}\" and \"{fact2}\"—how does that relate to your answer?"
            ]

        # decide which level to use
        lvl = min(c, 2)
        # if Level 3 but not enough facts, fallback to Level 2
        if lvl == 2 and len(facts) < 2:
            lvl = 1

        counts[section] = c + 1
        return levels[lvl]

    def ask(self, session_id: str, user_message: str) -> str:
        lang = detect_language(user_message)

        # 1) Non‐answer check → clarifier
        if not is_valid_answer(user_message):
            last = self.awaiting.get(session_id)
            if last:
                return self._tiered_clarifier(session_id, last, lang)
            # generic empathic probe
            if lang == 'ar':
                return "أسمعك، لكني أريد أن أفهم أكثر. كيف تشعر بالضبط الآن؟"
            else:
                return "I hear you, but I’d like to understand better—how are you feeling right now?"

        # 2) Initialize session state
        self.interviewer.init_session(session_id)
        self.histories.setdefault(session_id, [])

        # 3) Structured interview phase
        if not self.interviewer.is_complete(session_id):
            last = self.awaiting.get(session_id)
            # if we just asked, check relevance & record
            if last:
                # pick q_text in proper language
                q_text = (AR_SECTION_QUESTIONS if lang=='ar' else SECTION_QUESTIONS)[last]
                sim    = self._semantic_similarity(q_text, user_message)
                ok_sim = sim >= 0.3
                ok_cls = self._classify_answer(q_text, user_message, lang)
                if not (ok_sim and ok_cls):
                    return self._tiered_clarifier(session_id, last, lang)

                # record valid answer, reset clarifier count
                self.interviewer.record_response(session_id, user_message)
                self.clarify_counts[session_id].pop(last, None)

            # ask next section
            nxt = self.interviewer.next_section(session_id)
            q   = (AR_SECTION_QUESTIONS if lang=='ar' else SECTION_QUESTIONS)[nxt]
            if lang == 'ar':
                prompt = ("مرحبًا! أنا El Consulto، طبيبك النفسي الافتراضي. "
                          if last is None else "شكرًا لمشاركتك. ") + q
            else:
                prompt = ("Hello! I’m El Consulto, your virtual psychiatrist. "
                          if last is None else "Thank you for sharing. ") + q

            self.awaiting[session_id] = nxt
            return prompt

        # 4) Free‐form therapy phase
        sheet = self.interviewer.get_sheet(session_id)
        sheet_text = "\n".join(f"{k.replace('_',' ').title()}: {v}"
                               for k,v in sheet.items())
        notes      = self.mem.retrieve(session_id, user_message, k=3)
        mem_block  = ("\n".join(notes) + "\n\n") if notes else ""

        if lang == 'ar':
            sys_prompt = (
                "أنت El Consulto، المعالج الودود. استخدم ورقة المعلومات "
                "لتقديم ردود موجزة وعملية. إذا ابتعد المريض، أعده بلطف."
            )
            err = "عذرًا، حدث خطأ. هل يمكنك المحاولة مرة أخرى؟"
        else:
            sys_prompt = (
                "You are El Consulto, a friendly psychiatrist AI. Use the patient sheet "
                "to craft concise, actionable responses. If the user drifts off-topic, gently guide them back."
            )
            err = "Sorry, something went wrong. Could you try again?"

        msgs = [
            {"role":"system","content":sys_prompt},
            {"role":"system","content":"Patient Sheet:\n"+sheet_text}
        ]
        msgs.extend(self.histories[session_id])
        msgs.append({"role":"user","content":mem_block+user_message})

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=msgs,
                max_tokens_to_sample=250,
                temperature=0.7
            )
            answer = resp.choices[0].message.content.strip()
        except Exception:
            return err

        # record conversation & memory
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
    # smoke‐test
    for inp in ["hahaha", "k", "I feel stuck at work", "مساء الخير", "مش فاهم حاجة"]:
        print("User:", inp)
        print("Bot :", agent.ask("demo", inp))
        print()
