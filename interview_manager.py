# interview_manager.py

from typing import Dict, Optional

# Our sheet template
SCHEMA_TEMPLATE = {
    "personal_info": None,
    "chief_complaint": None,
    "history_present_illness": None,
    "past_psychiatric_history": None,
    "medical_history": None,
    "surgical_history": None,
    "family_history": None,
    "substance_use_history": None,
    "psychological_assessment": None,
    "mental_state_exam": None,
    "formulation": None,
    "provisional_diagnosis": None,
}

# Natural language prompts to gather each section
SECTION_QUESTIONS = {
    "personal_info":
        "To begin, please tell me a bit about yourself: your age, occupation, living situation, "
        "and anything else you’d like me to know about who you are right now.",
    "chief_complaint":
        "What is the main issue that brings you here today? In your own words, please describe "
        "what’s most concerning you.",
    "history_present_illness":
        "Can you walk me through how this issue has developed over time? Describe when it started, "
        "how it’s changed, and any triggers you’ve noticed.",
    "past_psychiatric_history":
        "Have you ever experienced similar difficulties in the past or worked with a mental health "
        "professional before? Share any relevant history.",
    "medical_history":
        "Tell me about your medical history—any chronic conditions, medications, surgeries, or "
        "ongoing treatments.",
    "surgical_history":
        "Are there any surgeries you’ve undergone that you think might be important for me to know?",
    "family_history":
        "Does mental health or any medical condition run in your family? Please share what you’re "
        "comfortable disclosing.",
    "substance_use_history":
        "Have you used alcohol, tobacco, or any recreational or prescription substances? Let me know "
        "about frequency and any concerns.",
    "psychological_assessment":
        "I’d like to understand your personality and coping style. Have you ever taken assessments "
        "like MBTI or similar? If not, describe your typical ways of thinking, feeling, and behaving.",
    "mental_state_exam":
        "Right now, how would you describe your mood, thoughts, and overall mental state? Are you "
        "feeling anxious, calm, motivated, etc.?",
    "formulation":
        "Based on what you’ve shared, how would you explain why these difficulties are happening? "
        "This can be in your own words.",
    "provisional_diagnosis":
        "Given all of this, what label or name feels closest to describing your experience (for "
        "example, anxiety, depression, OCD)? If you’re unsure, it’s okay to say so.",
}

class InterviewManager:
    """
    Drives a structured interview:
    1) Keeps a per-session sheet
    2) Knows which section comes next
    3) Records user answers
    4) Knows when the sheet is complete
    """
    def __init__(self):
        # session_id -> dict of section -> answer
        self.sessions: Dict[str, Dict[str, Optional[str]]] = {}

    def init_session(self, session_id: str):
        if session_id not in self.sessions:
            # deep copy template
            self.sessions[session_id] = {k: None for k in SCHEMA_TEMPLATE}

    def next_section(self, session_id: str) -> Optional[str]:
        """Return the next section key that is still None, or None if complete."""
        self.init_session(session_id)
        for key, val in self.sessions[session_id].items():
            if val is None:
                return key
        return None

    def get_question(self, session_id: str) -> Optional[str]:
        """
        Return the natural-language question for the next section,
        or None if the sheet is complete.
        """
        sec = self.next_section(session_id)
        if sec:
            return SECTION_QUESTIONS.get(sec)
        return None

    def record_response(self, session_id: str, user_message: str):
        """
        Save the user’s answer under the section that was just asked.
        """
        sec = self.next_section(session_id)
        if sec:
            # record response and advance
            self.sessions[session_id][sec] = user_message

    def is_complete(self, session_id: str) -> bool:
        self.init_session(session_id)
        return all(v is not None for v in self.sessions[session_id].values())

    def get_sheet(self, session_id: str) -> Dict[str, Optional[str]]:
        self.init_session(session_id)
        return self.sessions[session_id]
