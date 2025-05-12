# interview_manager.py

from typing import Dict, Optional

# —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
# Define your main section prompts here to avoid any circular imports
SECTION_QUESTIONS: Dict[str, str] = {
    "personal_info":           "To begin, please tell me a bit about yourself: your age, occupation, living situation, etc.",
    "chief_complaint":         "What is the main issue that brings you here today? In your own words, please describe what’s most concerning you.",
    "history_present_illness": "Can you walk me through how this issue has developed over time? Describe when it started, how it’s changed, and any triggers you’ve noticed.",
    "past_psychiatric_history": "Have you ever experienced similar difficulties in the past or worked with a mental health professional before? Share any relevant history.",
    "medical_history":         "Tell me about your medical history—any chronic conditions, medications, surgeries, or ongoing treatments.",
    "surgical_history":        "Are there any surgeries you’ve undergone that you think might be important for me to know?",
    "family_history":          "Does mental health or any medical condition run in your family? Please share what you’re comfortable disclosing.",
    "substance_use_history":   "Have you used alcohol, tobacco, or any recreational or prescription substances? Let me know about frequency and any concerns.",
    "psychological_assessment":"I’d like to understand your personality and coping style. Have you ever taken assessments like MBTI or similar? If not, describe your typical ways of thinking, feeling, and behaving.",
    "mental_state_exam":       "Right now, how would you describe your mood, thoughts, and overall mental state? Are you feeling anxious, calm, motivated, etc.?",
    "formulation":             "Based on what you’ve shared, how would you explain why these difficulties are happening? This can be in your own words.",
    "provisional_diagnosis":   "Given all of this, what label or name feels closest to describing your experience (for example, anxiety, depression, OCD)? If you’re unsure, it’s okay to say so."
}

# —––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––—
# The rest of your InterviewManager implementation (multi‐subfield logic, etc.)
# remains exactly as before—just remove any `from interview_manager import SECTION_QUESTIONS`.
# For example:

SECTIONS = [
    "personal_info","chief_complaint","history_present_illness",
    "past_psychiatric_history","medical_history","surgical_history",
    "family_history","substance_use_history","psychological_assessment",
    "mental_state_exam","formulation","provisional_diagnosis",
]

SUBFIELDS = {
    "history_present_illness": [
        "onset","course","severity","triggers","functional_impact","additional_details"
    ]
}
for sec in SECTIONS:
    if sec not in SUBFIELDS:
        SUBFIELDS[sec] = ["main","additional_details"]

TITLES = {
    sec: sec.replace("_"," ").title() for sec in SECTIONS
}

# Build your multilingual QUESTIONS dict exactly as you had it,
# using SECTION_QUESTIONS[sec] for the "main" subfield prompt.
# ...

class InterviewManager:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Dict[str, Optional[str]]]] = {}

    def init_session(self, session_id: str):
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                sec: {f: None for f in SUBFIELDS[sec]} for sec in SECTIONS
            }

    def next_field(self, session_id: str):
        self.init_session(session_id)
        for sec in SECTIONS:
            for fld in SUBFIELDS[sec]:
                if self.sessions[session_id][sec][fld] is None:
                    return sec, fld
        return None, None

    def get_prompt(self, session_id: str, lang: str = "en") -> str:
        sec, fld = self.next_field(session_id)
        if not sec:
            return None
        # Assume you have a QUESTIONS dict mapping sec→fld→{'en':…, 'ar':…}
        return QUESTIONS[sec][fld][lang]

    def record_response(self, session_id: str, section: str, subfield: str, answer: str):
        self.sessions[session_id][section][subfield] = answer

    def is_complete(self, session_id: str) -> bool:
        self.init_session(session_id)
        return all(
            self.sessions[session_id][sec][fld] is not None
            for sec in SECTIONS for fld in SUBFIELDS[sec]
        )

    def get_flat_sheet(self, session_id: str) -> str:
        self.init_session(session_id)
        lines = []
        for sec in SECTIONS:
            for fld in SUBFIELDS[sec]:
                val = self.sessions[session_id][sec][fld]
                if val:
                    label = f"{sec.replace('_',' ').title()} [{fld}]"
                    lines.append(f"{label}: {val}")
        return "\n".join(lines)
