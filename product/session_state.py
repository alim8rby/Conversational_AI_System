"""Read-only projection of structured conversation state."""

from interview_manager import InterviewManager, SECTIONS, SUBFIELDS


def build_session_state(
    manager: InterviewManager,
    session_id: str,
    *,
    intake_enabled: bool = True,
    assistant_name: str = "",
) -> dict:
    if not intake_enabled:
        return {
            "schema_version": "session-state-v1",
            "session_id": session_id,
            "status": "ready",
            "assistant": assistant_name,
            "progress": {
                "completed_fields": 0,
                "total_fields": 0,
                "completion_rate": 0.0,
            },
            "current": {
                "section": None,
                "field": None,
            },
            "sections": [],
        }

    manager.init_session(session_id)
    section, field = manager.next_field(session_id)
    session = manager.sessions[session_id]

    sections = []
    completed_fields = 0
    total_fields = 0

    for name in SECTIONS:
        fields = []
        for field_name in SUBFIELDS[name]:
            total_fields += 1
            value = session[name][field_name]
            completed = value is not None
            completed_fields += completed
            fields.append({
                "field": field_name,
                "completed": completed,
            })
        sections.append({
            "section": name,
            "completed": all(item["completed"] for item in fields),
            "fields": fields,
        })

    return {
        "schema_version": "session-state-v1",
        "session_id": session_id,
        "status": "complete" if manager.is_complete(session_id) else "in_progress",
        "progress": {
            "completed_fields": completed_fields,
            "total_fields": total_fields,
            "completion_rate": completed_fields / total_fields if total_fields else 1.0,
        },
        "current": {
            "section": section,
            "field": field,
        },
        "sections": sections,
    }
