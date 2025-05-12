# interview_manager.py

from typing import Dict, Optional

# Define the order of your sections
SECTIONS = [
    "personal_info",
    "chief_complaint",
    "history_present_illness",
    "past_psychiatric_history",
    "medical_history",
    "surgical_history",
    "family_history",
    "substance_use_history",
    "psychological_assessment",
    "mental_state_exam",
    "formulation",
    "provisional_diagnosis",
]

# Sub-fields for each section.
# HPI gets a rich set; others get [main, additional_details]
SUBFIELDS = {
    "history_present_illness": [
        "onset", "course", "severity", "triggers", "functional_impact", "additional_details"
    ]
}
for sec in SECTIONS:
    if sec not in SUBFIELDS:
        SUBFIELDS[sec] = ["main", "additional_details"]

# Human‐friendly section titles for "additional_details" prompts
TITLES = {
    "personal_info": "personal information",
    "chief_complaint": "chief complaint",
    "history_present_illness": "history of present illness",
    "past_psychiatric_history": "past psychiatric history",
    "medical_history": "medical history",
    "surgical_history": "surgical history",
    "family_history": "family history",
    "substance_use_history": "substance use history",
    "psychological_assessment": "psychological assessment",
    "mental_state_exam": "current mental state",
    "formulation": "formulation",
    "provisional_diagnosis": "provisional diagnosis",
}

# Multilingual question templates
# For brevity we’ll show English + Arabic; Franco-Arab uses the Arabic TTS to speak romanized text
QUESTIONS = {}

for sec in SECTIONS:
    QUESTIONS[sec] = {}
    for field in SUBFIELDS[sec]:
        # defaults
        en = ""
        ar = ""
        if sec == "history_present_illness":
            # detailed HPI
            if field == "onset":
                en = "When did this issue begin?"
                ar = "متى بدأت هذه المشكلة؟"
            elif field == "course":
                en = "How has it changed over time?"
                ar = "كيف تطورت مع مرور الوقت؟"
            elif field == "severity":
                en = "On a scale of 1 to 10, how severe is it?"
                ar = "على مقياس من 1 إلى 10، ما مدى شدتها؟"
            elif field == "triggers":
                en = "What seems to trigger or worsen it?"
                ar = "ما العوامل التي تزيدها أو تفاقمها؟"
            elif field == "functional_impact":
                en = "How is this affecting your daily life?"
                ar = "كيف تؤثر على حياتك اليومية؟"
            else:  # additional_details
                en = "Is there anything else about this issue you’d like to share?"
                ar = "هل هناك أي تفاصيل أخرى تود مشاركتها عن هذه المشكلة؟"
        else:
            # generic two‐step flow
            if field == "main":
                # we’ll reuse SECTION_QUESTIONS for main
                # fill later from user’s system
                en = None
                ar = None
            else:
                title = TITLES[sec]
                en = f"Is there anything else about your {title} you’d like to add?"
                ar = f"هل هناك أي شيء آخر حول {TITLES[sec]} تريد إضافته؟"
        QUESTIONS[sec][field] = {"en": en, "ar": ar}

# Import SECTION_QUESTIONS from your previous code as English main‐questions
from interview_manager import SECTION_QUESTIONS as MAIN_QS  # adjust import path

# Fill in the 'main' entries
for sec in SECTIONS:
    QUESTIONS[sec]["main"]["en"] = MAIN_QS[sec]
    QUESTIONS[sec]["main"]["ar"] = {
        # Arabic translations of MAIN_QS:
        "personal_info":           "لنبدأ بالتعريف عن نفسك: عمرك، وظيفتك، وظروف معيشتك.",
        "chief_complaint":         "ما المشكلة الرئيسية التي جلبتك اليوم؟",
        "history_present_illness": "أخبرني كيف بدأت هذه المشكلة ولماذا أنت هنا الآن.",
        "past_psychiatric_history":"هل تعاملت مع طبيب نفسي أو مررت بأعراض مماثلة من قبل؟",
        "medical_history":         "أخبرني عن تاريخك الطبي: أمراض أو أدوية أو علاجات.",
        "surgical_history":        "هل أجريت أي عمليات جراحية مهمة؟",
        "family_history":          "هل لديك تاريخ مرضي أو نفسي في العائلة؟",
        "substance_use_history":   "هل استخدمت الكحول أو أي مواد أخرى؟",
        "psychological_assessment":"هل أجريت أي اختبارات نفسية مثل MBTI؟",
        "mental_state_exam":       "كيف تصف حالتك الذهنية الآن؟",
        "formulation":             "كيف تفسر سبب هذه المشكلات؟",
        "provisional_diagnosis":   "ما التشخيص التقريبي الذي تشعر أنه مناسب؟",
    }[sec]

class InterviewManager:
    """
    Manages a multi‐subfield, multi‐section interview:
    - Tracks answers per (section, subfield)
    - Knows which prompt to ask next
    - Knows when all data is collected
    """
    def __init__(self):
        # session_id → section → subfield → answer(str)
        self.sessions: Dict[str, Dict[str, Dict[str, Optional[str]]]] = {}

    def init_session(self, session_id: str):
        if session_id not in self.sessions:
            # deep‐copy template
            self.sessions[session_id] = {
                sec: {f: None for f in SUBFIELDS[sec]}
                for sec in SECTIONS
            }

    def next_field(self, session_id: str):
        """Return (section, subfield) for the next unanswered field, or (None,None)."""
        self.init_session(session_id)
        for sec in SECTIONS:
            for fld in SUBFIELDS[sec]:
                if self.sessions[session_id][sec][fld] is None:
                    return sec, fld
        return None, None

    def get_prompt(self, session_id: str, lang: str = "en") -> str:
        """
        Returns the localized question for the next field,
        or None if the interview is fully complete.
        """
        sec, fld = self.next_field(session_id)
        if not sec:
            return None
        text = QUESTIONS[sec][fld][lang]
        return text

    def record_response(self, session_id: str, section: str, subfield: str, answer: str):
        """Store the user's answer in the appropriate slot."""
        self.sessions[session_id][section][subfield] = answer

    def is_complete(self, session_id: str) -> bool:
        """True iff every (section, subfield) has a non‐None answer."""
        self.init_session(session_id)
        for sec in SECTIONS:
            for fld in SUBFIELDS[sec]:
                if self.sessions[session_id][sec][fld] is None:
                    return False
        return True

    def get_flat_sheet(self, session_id: str) -> str:
        """Flatten all collected data into a summary block."""
        self.init_session(session_id)
        lines = []
        for sec in SECTIONS:
            for fld in SUBFIELDS[sec]:
                val = self.sessions[session_id][sec][fld]
                if val:
                    label = f"{sec.replace('_',' ').title()} [{fld}]"
                    lines.append(f"{label}: {val}")
        return "\n".join(lines)
