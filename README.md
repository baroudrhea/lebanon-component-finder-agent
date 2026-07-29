# Lebanon Electronics Component Finder

Homework 2 (AI Agents) - Rhea Baroud

You tell it an electronics component you need, and it searches for stores in Lebanon that might sell it, checks how far the store is from you, and saves everything to a text file.

Built with Gemini (google-genai library) using 3 tools:
- `search_component_stores` - searches the web for the part
- `check_distance` - checks distance from you to the store area
- `save_summary` - saves the results to a .txt file

## how to run

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

uses gemini-3-flash-preview.
