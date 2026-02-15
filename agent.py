"""Profile agent: RAG-powered persona that answers questions about the profile."""

import os

from openai import OpenAI

from rag import ProfileRAG
from tools import build_tools, handle_tool_call


def _extract_content(content) -> str:
    """Extract plain text from Gradio message content (str or multimodal list)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                return item.get("text", "")
            if isinstance(item, str):
                return item
        return ""
    return ""


def _gradio_history_to_messages(history: list) -> list[dict]:
    """Convert Gradio chat history to OpenAI messages format."""
    messages = []
    for msg in history:
        if not isinstance(msg, dict) or "role" not in msg:
            continue
        role = msg["role"]
        content = _extract_content(msg.get("content", ""))
        if content:
            messages.append({"role": role, "content": content})
    return messages


def _truncate_history(messages: list[dict], max_turns: int) -> list[dict]:
    """Keep only the last max_turns user/assistant pairs."""
    if max_turns <= 0 or len(messages) <= max_turns * 2:
        return messages
    return messages[-(max_turns * 2) :]


class Me:
    """Profile agent that answers as the person, using RAG for profile context."""

    def __init__(self):
        self.name = os.getenv("PERSON_NAME", "Abiddhanani")
        self.openai = OpenAI()

        summary_path = os.getenv("SUMMARY_PATH", "me/summary.txt")
        resume_pdf = os.getenv("RESUME_PDF", "me/AbidDhanani.pdf")
        chunk_size = int(os.getenv("RAG_CHUNK_SIZE", "600"))
        chunk_overlap = int(os.getenv("RAG_CHUNK_OVERLAP", "100"))
        retrieval_k = int(os.getenv("RAG_RETRIEVAL_K", "5"))
        self.max_history_turns = int(os.getenv("MAX_HISTORY_TURNS", "10"))

        self.rag = ProfileRAG(
            summary_path=summary_path,
            resume_pdf=resume_pdf,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        self.tools_json, self.tool_fns = build_tools(
            self.rag,
            self.name,
            retrieval_k=retrieval_k,
        )

    def _system_prompt(self) -> str:
        return (
            f"You are acting as {self.name}. You are answering questions on {self.name}'s website, "
            "particularly questions related to career, background, skills and experience. "
            f"Your responsibility is to represent {self.name} for interactions on the website as faithfully as possible. "
            "Use the search_profile tool to find relevant information from the summary and resume before answering questions. "
            "Be professional and engaging, as if talking to a potential client or future employer. "
            "If you don't know the answer to any question, use record_unknown_question to record it. "
            "If the user is engaging, try to steer them towards getting in touch; ask for their email and use record_user_details. "
            f"With this in mind, chat with the user, always staying in character as {self.name}."
        )

    def chat(self, message: str, history: list) -> str:
        """Handle a chat message; history is Gradio 5 format [{"role": ..., "content": ...}, ...]."""
        api_messages = _gradio_history_to_messages(history)
        api_messages = _truncate_history(api_messages, self.max_history_turns)
        api_messages.append({"role": "user", "content": message})

        messages = [{"role": "system", "content": self._system_prompt()}] + api_messages
        done = False

        while not done:
            response = self.openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=self.tools_json,
            )
            msg = response.choices[0].message

            if response.choices[0].finish_reason == "tool_calls":
                messages.append(msg)
                for tc in msg.tool_calls:
                    result = handle_tool_call(tc, self.tool_fns)
                    print(f"Tool called: {tc.function.name}", flush=True)
                    messages.append(result)
            else:
                done = True

        return msg.content or ""
