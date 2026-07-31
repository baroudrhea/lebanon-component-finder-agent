# Lebanon Electronics Component Finder

Homework 2 & 3 (AI Agents) - Rhea Baroud

As a CCE student, I find it hard to find specific electronics parts in Lebanon since most stores here don't have organized online inventories. So this agent does that searching for you: you tell it a component you need, and it searches for stores in Lebanon that might sell it, checks how far the store is from you, and saves everything to a text file. Now it also remembers what you searched for before, even after closing it.

Built with Gemini (google-genai library) using 3 tools:
- `search_component_stores` - searches the web for the part
- `check_distance` - checks distance from you to the store area
- `save_summary` - saves the results to a .txt file

## what's new for HW3

- added memory that sticks around between runs, saved in `agent_memory.json`
- added a proper chat interface using Gradio (`app.py`) instead of just the terminal

## how to run (terminal)

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

## how to run (web version)

same setup as above, then:
```
python app.py
```
it'll give you a local link (something like `http://127.0.0.1:7860`), open that in your browser and chat with it there instead.

uses gemini-flash-lite-latest.
