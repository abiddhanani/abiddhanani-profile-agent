"""Gradio chat interface for the profile agent."""

import sys
from pathlib import Path

# Ensure project root is on path (for gradio deploy / running from any cwd)
_root = Path(__file__).resolve().parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from dotenv import load_dotenv
import gradio as gr

load_dotenv(override=True)


def run():
    """Launch the Gradio chat interface."""
    try:
        from agent import Me
        me = Me()
        gr.ChatInterface(me.chat, type="messages", save_history=True).launch()
    except FileNotFoundError as e:
        with gr.Blocks(title="Profile Agent – Setup Required") as demo:
            gr.Markdown(f"## Setup required\n\n{e}\n\nAdd `me/summary.txt` and your resume PDF to this Space (see README).")
        demo.launch()
    except ModuleNotFoundError as e:
        import traceback
        msg = f"**Import error:** {e}\n\nRun from the project root (where `app.py` and `agent.py` live) or install the app as a package."
        print(msg, file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        with gr.Blocks(title="Profile Agent – Error") as demo:
            gr.Markdown(msg)
        demo.launch()


if __name__ == "__main__":
    run()
