"""Tools: record_user_details, record_unknown_question, search_profile."""

import json
import os
from typing import Callable

import requests


def push(text: str) -> None:
    """Send a push notification via Pushover."""
    token = os.getenv("PUSHOVER_TOKEN")
    user = os.getenv("PUSHOVER_USER")
    if token and user:
        requests.post(
            "https://api.pushover.net/1/messages.json",
            data={"token": token, "user": user, "message": text},
        )


def record_user_details(
    email: str,
    name: str = "Name not provided",
    notes: str = "not provided",
) -> dict:
    """Record a user who is interested in being in touch."""
    push(f"Recording {name} with email {email} and notes {notes}")
    return {"recorded": "ok"}


def record_unknown_question(question: str) -> dict:
    """Record a question that couldn't be answered."""
    push(f"Recording {question}")
    return {"recorded": "ok"}


def make_search_profile(rag, person_name: str, retrieval_k: int = 5) -> Callable:
    """Create a search_profile function bound to the given RAG."""

    def search_profile(query: str) -> str:
        result = rag.search(query, k=retrieval_k)
        if not result:
            return f"No relevant information found in {person_name}'s profile for that query."
        return result

    return search_profile


RECORD_USER_DETAILS_SCHEMA = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {"type": "string", "description": "The email address of this user"},
            "name": {"type": "string", "description": "The user's name, if they provided it"},
            "notes": {"type": "string", "description": "Any additional information about the conversation"},
        },
        "required": ["email"],
        "additionalProperties": False,
    },
}

RECORD_UNKNOWN_QUESTION_SCHEMA = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {"type": "string", "description": "The question that couldn't be answered"},
        },
        "required": ["question"],
        "additionalProperties": False,
    },
}


def search_profile_schema(person_name: str) -> dict:
    """Build the search_profile tool schema."""
    return {
        "name": "search_profile",
        "description": f"Search {person_name}'s summary and resume for relevant information. Use this before answering questions about {person_name}.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query - what you need to find out about the person"},
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    }


def build_tools(rag, person_name: str, retrieval_k: int = 5) -> tuple[list[dict], dict[str, Callable]]:
    """Build the tools list and a mapping of tool name -> callable."""
    search_fn = make_search_profile(rag, person_name, retrieval_k)
    tools_json = [
        {"type": "function", "function": search_profile_schema(person_name)},
        {"type": "function", "function": RECORD_USER_DETAILS_SCHEMA},
        {"type": "function", "function": RECORD_UNKNOWN_QUESTION_SCHEMA},
    ]
    tool_fns = {
        "search_profile": search_fn,
        "record_user_details": record_user_details,
        "record_unknown_question": record_unknown_question,
    }
    return tools_json, tool_fns


def handle_tool_call(tool_call, tool_fns: dict) -> dict:
    """Execute a single tool call and return the result message."""
    name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)
    fn = tool_fns.get(name)
    result = fn(**arguments) if fn else {}
    return {"role": "tool", "content": json.dumps(result), "tool_call_id": tool_call.id}
