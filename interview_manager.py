from typing import Dict, Optional, Tuple

SECTION_QUESTIONS: Dict[str, str] = {
    "personal_info": "Tell me a little about yourself, such as your age, occupation, and living situation.",
    "chief_complaint": "What is the main issue that brings you here today? Describe what concerns you most in your own words.",
    "history_present_illness": "Walk me through how this issue developed over time. When did it start, how has it changed, and what triggers have you noticed?",
    "past_psychiatric_history": "Have you experienced similar difficulties before or worked with a mental health professional?",
    "medical_history": "Tell me about relevant medical conditions, medications, surgeries, or ongoing treatments.",
    "surgical_history": "Are there any surgeries or major procedures that are important for me to know about?",
    "family_history": "Does mental or physical illness run in your family? Share what you are comfortable disclosing.",
    "substance_use_history": "Tell me about alcohol, tobacco, recreational substances, or prescription medicines you use, including frequency.",
    "psychological_assessment": "How would you describe your typical ways of thinking, feeling, coping, and behaving?",
    "mental_state_exam": "How would you describe your mood, thoughts, anxiety, energy, and overall mental state right now?",
    "formulation": "Based on what you have shared, how would you explain what may be contributing to these difficulties?",
    "provisional_diagnosis": "If you had to give your experience a name or label, what would feel closest? It is fine to be unsure.",
}

SECTIONS = list(SECTION_QUESTIONS)
SUBFIELDS = {
    "history_present_illness": ["onset", "course", "severity", "triggers", "functional_impact", "additional_details"]
}
for section in SECTIONS:
    SUBFIELDS.setdefault(section, ["main", "additional_details"])

SUBFIELD_LABELS = {
    "onset": "When did it start, and what was happening around that time?",
    "course": "How has it changed since it started?",
    "severity": "How intense or disruptive is it, and how often does it occur?",
    "triggers": "What tends to trigger, worsen, or relieve it?",
    "functional_impact": "How does it affect your work, relationships, routines, or daily functioning?",
    "additional_details": "Is there anything else important about this area that you would like to add?",
}

class InterviewManager:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Dict[str, Optional[str]]]] = {}

    def init_session(self, session_id: str) -> None:
        self.sessions.setdefault(
            session_id,
            {section: {field: None for field in SUBFIELDS[section]} for section in SECTIONS},
        )

    def next_field(self, session_id: str) -> Tuple[Optional[str], Optional[str]]:
        self.init_session(session_id)
        for section in SECTIONS:
            for field in SUBFIELDS[section]:
                if self.sessions[session_id][section][field] is None:
                    return section, field
        return None, None

    def get_prompt(self, session_id: str, lang: str = "en") -> Optional[str]:
        section, field = self.next_field(session_id)
        if not section:
            return None
        if field == "main":
            prompt = SECTION_QUESTIONS[section]
        else:
            prompt = SUBFIELD_LABELS.get(field, SECTION_QUESTIONS[section])
        if lang == "ar":
            return self._arabic_prompt(section, field, prompt)
        return prompt

    @staticmethod
    def _arabic_prompt(section: str, field: str, fallback: str) -> str:
        arabic = {
            "personal_info": "احكي لي قليلاً عن نفسك، مثل سنك وشغلك ووضعك المعيشي.",
            "chief_complaint": "ما المشكلة الأساسية التي جعلتك تطلب المساعدة اليوم؟ احكي عنها بطريقتك.",
            "history_present_illness": "احكي لي كيف بدأت المشكلة وتطورت مع الوقت، وهل لاحظت أي محفزات.",
            "past_psychiatric_history": "هل مررت بمشكلة مشابهة من قبل أو تعاملت مع متخصص في الصحة النفسية؟",
            "medical_history": "احكي لي عن أي أمراض مزمنة أو أدوية أو علاجات مهمة.",
            "surgical_history": "هل أجريت أي عمليات أو إجراءات طبية مهمة؟",
            "family_history": "هل توجد أمراض نفسية أو جسدية في العائلة؟",
            "substance_use_history": "احكي لي عن استخدامك للتدخين أو الكحول أو أي مواد أو أدوية أخرى.",
            "psychological_assessment": "كيف تصف عادةً طريقة تفكيرك ومشاعرك وطريقة تعاملك مع الضغوط؟",
            "mental_state_exam": "كيف تصف مزاجك وأفكارك وقلقك وطاقة جسمك وحالتك النفسية الآن؟",
            "formulation": "من وجهة نظرك، ما الذي قد يكون وراء الصعوبات التي تمر بها؟",
            "provisional_diagnosis": "لو أردت أن تسمي تجربتك باسم أو وصف، ما الأقرب لها؟ وممكن تكون غير متأكد.",
        }
        return arabic.get(section, fallback)

    def record_response(self, session_id: str, section: str, subfield: str, answer: str) -> None:
        self.init_session(session_id)
        self.sessions[session_id][section][subfield] = answer

    def is_complete(self, session_id: str) -> bool:
        self.init_session(session_id)
        return all(
            self.sessions[session_id][section][field] is not None
            for section in SECTIONS for field in SUBFIELDS[section]
        )

    def get_flat_sheet(self, session_id: str) -> str:
        self.init_session(session_id)
        lines = []
        for section in SECTIONS:
            for field in SUBFIELDS[section]:
                value = self.sessions[session_id][section][field]
                if value:
                    label = f"{section.replace('_', ' ').title()} [{field}]"
                    lines.append(f"{label}: {value}")
        return "\n".join(lines)
