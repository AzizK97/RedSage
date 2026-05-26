import re
from psycopg import Connection

from app.repositories.thread_message_repository import ThreadMessageRepository
from app.repositories.thread_repository import ThreadRepository


def _extract_smart_title(user_text: str, assistant_text: str) -> str:
    """Extract a contextual title from combined user and assistant messages using heuristics."""
    combined = f"{user_text} {assistant_text}".lower()
    
    # Common action patterns
    action_keywords = {
        r"\b(create|add|new)\s+": "Create",
        r"\b(update|edit|modify|change|set)\s+": "Update",
        r"\b(delete|remove|drop)\s+": "Delete",
        r"\b(list|show|get|fetch|retrieve|view|display)\s+": "List",
        r"\b(report|summary|summarize|analyze)\s+": "Report",
        r"\b(assign|reassign)\s+": "Assign",
        r"\b(close|resolve|complete)\s+": "Close",
        r"\b(bulk|batch)\s+": "Bulk",
    }
    
    # Entity patterns
    entity_patterns = {
        r"project[s]?\s+(?:named\s+)?['\"]?([^'\",.;!?]+)": "project",
        r"issue[s]?\s+(?:named\s+)?['\"]?([^'\",.;!?]+)": "issue",
        r"version[s]?\s+(?:named\s+)?['\"]?([^'\",.;!?]+)": "version",
        r"assignee[s]?\s+([A-Z][a-z]+)": "assignee",
        r"tracker[s]?\s+([A-Z][a-z]+)": "tracker",
        r"status[:\s]+([A-Z][a-z]+)": "status",
    }
    
    detected_action = None
    detected_entity = None
    
    # Find action
    for pattern, action in action_keywords.items():
        if re.search(pattern, combined):
            detected_action = action
            break
    
    # Find entity type and name
    for pattern, entity_type in entity_patterns.items():
        match = re.search(pattern, combined, re.IGNORECASE)
        if match:
            entity_name = match.group(1).strip().strip("'\"")
            # Trim entity name to reasonable length
            if len(entity_name) > 20:
                entity_name = entity_name[:20] + "…"
            detected_entity = entity_name
            break
    
    # Build title from detected components
    if detected_action and detected_entity:
        title = f"{detected_action} {detected_entity}"
    elif detected_action:
        # Try to find object after action (word immediately following)
        action_obj_match = re.search(r"\b(create|update|list|delete|assign|close)\s+(\w+)", combined)
        if action_obj_match:
            obj = action_obj_match.group(2).capitalize()
            title = f"{detected_action} {obj}"
        else:
            title = detected_action
    elif detected_entity:
        # If only entity, use first 42 chars of user message
        first_msg = user_text.replace("\n", " ").replace("\s+", " ").strip()
        title = first_msg if first_msg else "New conversation"
    else:
        # Fallback to original user message  
        title = user_text.replace("\n", " ").replace("\s+", " ").strip()
    
    # Trim to 42 chars
    if len(title) > 42:
        title = title[:41] + "…"
    
    return title if title else "New conversation"


def _trim_title(text: str, max_len: int = 42) -> str:
    compact = " ".join(text.split()).strip()
    if not compact:
        return "New conversation"
    if len(compact) <= max_len:
        return compact
    return f"{compact[: max_len - 1]}…"


def _trim_preview(text: str, max_len: int = 70) -> str:
    compact = " ".join(text.split()).strip()
    if not compact:
        return "No messages yet"
    if len(compact) <= max_len:
        return compact
    return f"{compact[: max_len - 1]}…"


def ensure_thread_tables(db: Connection) -> None:
    ThreadRepository(db).ensure_table()
    ThreadMessageRepository(db).ensure_table()


def persist_user_and_assistant(
    db: Connection,
    thread_id: str,
    user_text: str,
    assistant_text: str,
) -> None:
    messages = ThreadMessageRepository(db)
    threads = ThreadRepository(db)
    messages.append(thread_id, "user", user_text)
    messages.append(thread_id, "assistant", assistant_text)
    title = _extract_smart_title(user_text, assistant_text)
    preview = _trim_preview(assistant_text)
    threads.update_metadata(thread_id, title, preview)


def persist_assistant_only(
    db: Connection,
    thread_id: str,
    assistant_text: str,
) -> None:
    messages = ThreadMessageRepository(db)
    threads = ThreadRepository(db)
    messages.append(thread_id, "assistant", assistant_text)
    preview = _trim_preview(assistant_text)
    threads.update_preview(thread_id, preview)
