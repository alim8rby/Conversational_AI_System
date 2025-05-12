# -*- coding: utf-8 -*-
import os
import re
import math
from together import Together, error as ta_errors
from memory.memory_manager import MemoryManager
from interview_manager import InterviewManager, SECTION_QUESTIONS

def detect_language(text: str) -> str:
    if re.search(r'[\u0600-\u06FF]', text):
        return 'ar'
    if re.search(r'\d', text):
        return 'ar'   # Franco-Arab also uses Arabic TTS/LLM
    return 'en'

def is_valid_answer(text: str) -> bool:
    t = text.strip().lower()
    # reject pure laughter or single letters / very brief
    if re.fullmatch(r'(ha)+h?', t) or re.fullmatch(r'(heh)+', t) or len(t) <= 2:
        return False
    return len(t) >= 5  # allow slightly shorter now

class ConversationAgent:
    def __init__(self, model_name: str, embed_model: str, index_name: str):
        self.client   = Together(api_key=os.getenv("TOGETHER_API_KEY"))
        self.model    = model_name
        self.mem      = MemoryManager(embed_model, index_name)

        self.interviewer    = InterviewManager()
        self.awaiting       = {}  # session_id → (section, subfield)
        self.histories      = {}  # session_id → chat history list
        self.clarify_counts = {}  # session_id → {(section,subfield): count}

    def _semantic_similarity(self, q: str, a: str) -> float:
        try:
            resp = self.client.embeddings.create(
                model=self.mem.embed_model,
                input=[q, a]
            )
            vq, va = resp.data[0].embedding, resp.data[1].embedding
            dot = sum(x*y for x,y in zip(vq, va))
            mq = math.sqrt(sum(x*x for x in vq))
            ma = math.sqrt(sum(x*x for x in va))
            return dot/(mq*ma) if mq and ma else 0.0
        except:
            return 0.0  # on error, treat as not similar

    def _classify_answer(self, q: str, a: str, lang: str) -> bool:
        sys_prompt = (
            "أنت طبيب نفسي. هل تجيب الإجابة التالية على السؤال؟"
            if lang=='ar' else
            "You are a psychiatrist. Does the following answer address the question?"
        )
        try:
            r = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role":"system","content":sys_prompt},
                    {"role":"user","content":f"Question: {q}\nAnswer: {a}"}
                ],
                max_tokens_to_sample=3,
                temperature=0.0
            )
            ans = r.choices[0].message.content.strip().lower()
            return ans.startswith('نعم') or ans.startswith('yes')
        except:
            return False

    def _tiered_clarifier(self, session: str, sec: str, fld: str, lang: str) -> str:
        key = (session, sec, fld)
        cnt = self.clarify_counts.setdefault(key, 0)
        # gather two facts for level 3
        sheet = self.interviewer.get_flat_sheet(session).splitlines()
        fact1 = sheet[0] if len(sheet)>0 else ""
        fact2 = sheet[1] if len(sheet)>1 else ""

        levels_en = [
            "I’m sorry, I didn’t quite catch that. Could you tell me more?",
            "Sometimes feelings show up in our body—what do you notice physically right now?",
            f"You mentioned earlier \"{fact1}\" and \"{fact2}\"—how does that relate to your answer?"
        ]
        levels_ar = [
            "عذراً، لم أفهم تماماً. هل يمكنك التوضيح أكثر؟",
            "أحياناً تظهر المشاعر في الجسد—ماذا تشعر فيه جسدياً الآن؟",
            f"ذكرت سابقاً \"{fact1}\" و\"{fact2}\"—كيف يرتبط ذلك بردك؟"
        ]

        lvl = min(cnt, 2)
        self.clarify_counts[key] += 1
        return levels_ar[lvl] if lang=='ar' else levels_en[lvl]

    def ask(self, session_id: str, user_message: str) -> str:
        lang = detect_language(user_message)

        # 1) Non-answer → clarify
        if not is_valid_answer(user_message):
            sec, fld = self.awaiting.get(session_id, (None, None))
            if sec:
                return self._tiered_clarifier(session_id, sec, fld, lang)
            return ("أريد أن أفهم أكثر—كيف تشعر الآن؟" if lang=='ar'
                    else "I’d like to understand better—how are you feeling right now?")

        # 2) Init session state
        self.interviewer.init_session(session_id)
        self.histories.setdefault(session_id, [])

        # 3) Structured interview
        if not self.interviewer.is_complete(session_id):
            last = self.awaiting.get(session_id)
            if last[0]:
                q_text = self.interviewer.get_prompt(session_id, lang)
                sim    = self._semantic_similarity(q_text, user_message)
                cls_ok = self._classify_answer(q_text, user_message, lang)
                if sim < 0.3 or not cls_ok:
                    return self._tiered_clarifier(session_id, *last, lang)

                # record valid subfield answer
                self.interviewer.record_response(session_id, last[0], last[1], user_message)
                self.clarify_counts.pop((session_id, *last), None)

            # ask next
            sec, fld = self.interviewer.next_field(session_id)
            prompt    = self.interviewer.get_prompt(session_id, lang)
            greet     = "مرحباً!" if fld=="main" and lang=='ar' else "Hello!"    
            thank     = "شكراً لمشاركتك. " if fld!=" 'main'" and lang=='ar' else "Thank you for sharing. "

            text = (greet+" "+prompt) if fld=="main" else (thank+prompt)
            self.awaiting[session_id] = (sec, fld)
            return text

        # 4) Free-form therapy
        sheet = self.interviewer.get_flat_sheet(session_id)
        notes = self.mem.retrieve(session_id, user_message, k=3)
        mem   = "\n".join(notes)+"\n\n" if notes else ""

        sys_en = (
            "You are El Consulto, a friendly psychiatrist AI. Use the sheet to craft concise, actionable responses."
            " If the user drifts off-topic, gently bring them back."
        )
        sys_ar = (
            "أنت El Consulto، المعالج الودود. استخدم ورقة المعلومات "
            "لتقديم ردود موجزة وعملية. إذا ابتعد المريض عن الموضوع، أعده بلطف."
        )

        sys = sys_ar if lang=='ar' else sys_en
        err = "عفواً، حدث خطأ. حاول مرة أخرى." if lang=='ar' else "Sorry, something went wrong. Please try again."

        messages = [
            {"role":"system","content":sys},
            {"role":"system","content":"Patient Sheet:\n"+sheet},
        ]
        messages.extend(self.histories[session_id])
        messages.append({"role":"user","content":mem+user_message})

        try:
            resp   = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens_to_sample=250,
                temperature=0.7
            )
            answer = resp.choices[0].message.content.strip()
        except:
            return err

        # record final
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
    # Quick smoke
    for inp in ["hahaha","k","I feel stuck at work","مساء الخير","مش فاهم حاجة"]:
        print("User:",inp)
        print("Bot :",agent.ask("demo",inp))
        print()
