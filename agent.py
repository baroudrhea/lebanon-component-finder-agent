"""
Lebanon Electronics Component Finder Agent
--------------------------------------------
An AI agent that helps find electronics components for sale in Lebanon.
Built with Google's Gemini API using function calling (tool use).

Homework 2: AI Agents
"""

import os
import json
from datetime import datetime
from ddgs import DDGS

# =========================================================
# PERSISTENT MEMORY -- remembers past searches across separate
# runs of the program (long-term memory), unlike "contents" in
# the loop below which only remembers within ONE request.
# =========================================================
MEMORY_FILE = "agent_memory.json"


def load_memory() -> list:
    """
    Loads past search history from disk. Returns an empty list if
    no memory file exists yet (e.g. first time running the agent).
    """
    if not os.path.exists(MEMORY_FILE):
        return []
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_memory_entry(query: str, final_answer: str) -> None:
    """
    Appends one search to the persistent memory file, so future
    runs of the program (even after restarting) can reference it.
    """
    memory = load_memory()
    memory.append({
        "query": query,
        "answer": final_answer,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    # Keep only the most recent 20 entries so the file doesn't grow forever
    memory = memory[-20:]
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)


def format_memory_for_prompt(memory: list) -> str:
    """
    Turns the stored memory into a short block of text that gets
    added to the agent's instructions, so it can reference past
    searches (e.g. "you searched for this before on [date]").
    """
    if not memory:
        return "The user has no previous search history."

    recent = memory[-5:]  # only include the last 5 to keep the prompt short
    lines = ["Here is the user's recent search history:"]
    for entry in recent:
        lines.append(
            f"- On {entry['timestamp']}, asked: '{entry['query']}'"
        )
    return "\n".join(lines)


# =========================================================
# TOOL 1: Web search tool -- finds stores that might sell the part
# =========================================================
def search_component_stores(component_name: str) -> str:
    """
    Searches the web for stores in Lebanon that might carry the given
    electronics component. Lebanese electronics retailers often have no
    organized online inventory, so real answers usually come from forum
    posts, store social media, or general mentions -- not a clean catalog.
    """
    query = f"{component_name} electronics store Lebanon"

    try:
        results = DDGS().text(query, max_results=5)
    except Exception as e:
        return f"Search failed: {e}"

    if not results:
        return "No relevant results found."

    # Turn the raw search results into a short, readable summary
    lines = []
    for r in results:
        title = r.get("title", "")
        snippet = r.get("body", "")
        lines.append(f"- {title}: {snippet}")

    return "\n".join(lines)


# =========================================================
# TOOL 2: Distance tool -- estimates travel distance/time to a store area
# =========================================================
def check_distance(store_area: str, your_location: str) -> str:
    """
    Estimates how far a candidate store area is from the user's location.
    This turns a vague list of "here are some stores that might have it"
    into an actionable "here's the closest option first."

    (Simplified version: searches the web for travel time between the two
    locations, rather than using a paid mapping API -- keeps setup simple
    while still doing something the other two tools can't: real-world
    distance/time information.)
    """
    query = f"driving distance and time from {your_location} to {store_area}"

    try:
        results = DDGS().text(query, max_results=3)
    except Exception as e:
        return f"Distance search failed: {e}"

    if not results:
        return f"Could not find distance info for {store_area}."

    lines = [f"- {r.get('title', '')}: {r.get('body', '')}" for r in results]
    return "\n".join(lines)


# =========================================================
# TOOL 3: File tool -- saves a summary of the search results
# =========================================================
def save_summary(component_name: str, search_findings: str, distance_findings: str) -> str:
    """
    Saves a summary of the component search to a local text file.
    This is the agent's "memory" -- a durable output you can actually
    use later (e.g. on the errand to go buy the part), instead of
    just a chat reply that disappears when the conversation ends.
    """
    safe_name = component_name.replace(" ", "_").replace("/", "-")
    filename = f"component_search_{safe_name}.txt"

    content = (
        f"Component Search Summary\n"
        f"=========================\n"
        f"Component: {component_name}\n"
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        f"Store findings:\n{search_findings}\n\n"
        f"Distance/location findings:\n{distance_findings}\n"
    )

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    return f"Saved summary to {filename}"


# =========================================================
# THE AGENT LOOP
# input -> reason/decide -> act (call a tool) -> observe -> repeat
# =========================================================
from google import genai
from google.genai import types

# Maps the tool name Gemini asks for -> the actual Python function to run.
# This is the bridge between "the model requested a tool" and
# "code actually executes it" -- the model itself never runs these
# functions directly, it only ever asks for them by name.
AVAILABLE_TOOLS = {
    "search_component_stores": search_component_stores,
    "check_distance": check_distance,
    "save_summary": save_summary,
}

SYSTEM_INSTRUCTION = (
    "You are an agent that helps someone in Lebanon find electronics "
    "components. When asked about a component, first search for stores "
    "that might sell it. Then check the distance from the user's location "
    "to the most promising store area. Finally, save a summary of your "
    "findings to a file. Always end with a clear, short recommendation "
    "for the user in plain text."
)


def run_agent(user_message: str, api_key: str) -> str:
    """
    Runs the full agent loop for a single user request.
    This function IS the loop: it keeps calling Gemini, executing
    whatever tool Gemini asks for, and feeding the result back --
    until Gemini decides it has enough information and gives a
    final plain-text answer instead of another tool request.
    """
    client = genai.Client(api_key=api_key)

    # Load persistent memory and fold it into the instructions, so the
    # agent is aware of past searches even across separate program runs.
    memory = load_memory()
    memory_context = format_memory_for_prompt(memory)
    full_instruction = f"{SYSTEM_INSTRUCTION}\n\n{memory_context}"

    config = types.GenerateContentConfig(
        system_instruction=full_instruction,
        tools=[search_component_stores, check_distance, save_summary],
        # We turn OFF automatic function calling so we can see and control
        # every step of the loop ourselves -- this makes the reason/act/
        # observe cycle explicit instead of hidden inside the library.
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=True
        ),
    )

    # "contents" is the running conversation history sent to the model
    # each time. This IS the agent's short-term memory -- the model has
    # no memory of its own between calls, so we resend everything that's
    # happened so far on every single loop iteration.
    contents = [
        types.Content(role="user", parts=[types.Part(text=user_message)])
    ]

    max_iterations = 6  # safety limit so a bad response can't loop forever
    for step in range(max_iterations):
        response = client.models.generate_content(
            model="gemini-flash-lite-latest",
            contents=contents,
            config=config,
        )

        candidate = response.candidates[0]
        function_calls = [
            part.function_call
            for part in candidate.content.parts
            if part.function_call is not None
        ]

        if not function_calls:
            # No tool requested -> Gemini decided it has enough to answer.
            # Save this exchange to persistent memory before returning.
            save_memory_entry(user_message, response.text)
            return response.text

        # Add the model's own turn (its tool request) to the history
        contents.append(candidate.content)

        # Execute every requested tool call and feed the results back
        for fc in function_calls:
            tool_name = fc.name
            tool_args = dict(fc.args)
            print(f"[step {step + 1}] Agent is calling: {tool_name}({tool_args})")

            tool_function = AVAILABLE_TOOLS[tool_name]
            tool_result = tool_function(**tool_args)

            function_response_part = types.Part.from_function_response(
                name=tool_name,
                response={"result": tool_result},
            )
            contents.append(
                types.Content(role="user", parts=[function_response_part])
            )

    return "Reached the maximum number of steps without a final answer."


if __name__ == "__main__":
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise SystemExit(
            "Set your GEMINI_API_KEY environment variable before running."
        )

    print("Lebanon Electronics Component Finder Agent")
    print("Type a component you're looking for (or 'quit' to exit).\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit"):
            break
        answer = run_agent(user_input, api_key)
        print(f"\nAgent: {answer}\n")
