"""
Frontend for the Lebanon Electronics Component Finder Agent.
Built with Gradio -- wraps the existing run_agent() function from
agent.py in a simple web-based chat interface.

Homework 3: Foundry Models & Your Agent, v2 - Part B
"""

import os
import gradio as gr

from agent import run_agent


def chat_with_agent(message: str, history: list) -> str:
    """
    Gradio calls this function every time the user sends a message.
    'history' is Gradio's own chat history (for display purposes) --
    it's separate from our agent's own memory (contents/agent_memory.json).
    We just need to return the agent's reply as plain text.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "Error: GEMINI_API_KEY environment variable is not set."

    if not message.strip():
        return "Please type a component you're looking for."

    return run_agent(message, api_key)


demo = gr.ChatInterface(
    fn=chat_with_agent,
    title="Lebanon Electronics Component Finder",
    description=(
        "Tell me an electronics component you need and where you are "
        "(e.g. 'breadboard, I'm in Jeita'), and I'll search for stores "
        "in Lebanon, check the distance, and save a summary for you."
    ),
    examples=[
        "LM358 op-amp, I'm in Hamra",
        "Arduino Uno, I'm in Achrafieh",
        "10k resistor, I'm in Tripoli",
    ],
)

if __name__ == "__main__":
    demo.launch()
