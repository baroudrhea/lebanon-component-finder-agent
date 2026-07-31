# Lebanon Electronics Component Finder

Homework 2 & 3 (AI Agents) - Rhea Baroud

As an ECE student, I find it hard to find specific electronics parts in Lebanon since most stores here don't have organized online inventories. So this agent does that searching for you: you tell it a component you need, and it searches for stores in Lebanon that might sell it, checks how far the store is from you, and saves everything to a text file. It also remembers your past searches across separate runs.

Built with Gemini (google-genai library) using 3 tools:
- `search_component_stores` - searches the web for the part
- `check_distance` - checks distance from you to the store area
- `save_summary` - saves the results to a .txt file

## new in v2 (Homework 3)

- **Persistent memory** - the agent now remembers your past searches even after closing and reopening it. Past searches are saved to `agent_memory.json` and referenced in future conversations.
- **Web frontend** - added a Gradio-based chat interface (`app.py`) so you don't need the terminal anymore.

## how to run (command line)

```
pip install -r requirements.txt
```

set your free Gemini API key (get one at ai.google.dev):
- windows: `$env:GEMINI_API_KEY="yourkeyhere"`
- mac/linux: `export GEMINI_API_KEY=yourkeyhere`

then run:
```
python agent.py
```
and type the component you're looking for when it asks.

## how to run (web frontend)

Same setup as above (install requirements + set API key), then run:
```
python app.py
```
This opens a local web address (e.g. `http://127.0.0.1:7860`) - open it in your browser to use the chat interface instead of the terminal.

uses gemini-flash-lite-latest.
