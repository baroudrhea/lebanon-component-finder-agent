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

## HW4 — n8n Setup

### Self-hosting n8n

1. Install Docker Desktop
2. Run: 
docker volume create n8n_data
docker run -it --rm --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n docker.n8n.io/n8nio/n8n
3. Open http://localhost:5678 and create an owner account

## HW4 — Part B: Custom n8n Node 

Wrapped the HW2/HW3 agent as a custom n8n node. n8n nodes have to be written in TypeScript, so I bridged my Python agent with a small FastAPI service (agent_service/agent_api.py) that exposes run_agent() as an HTTP endpoint. The node calls that service, which calls the unmodified agent.py.

Flow: n8n workflow -> Component Finder Agent node -> FastAPI service -> agent.py -> Gemini

Note: n8n runs inside Docker, so the node can't reach the FastAPI service via localhost — it uses host.docker.internal instead, which lets the container reach the host machine.

### Running the FastAPI service
1. cd agent_service/
2. pip install -r requirements.txt
3. uvicorn agent_api:app --port 8000
4. Check http://localhost:8000/health returns {"status":"ok"}

### Building and installing the node
1. cd n8n-nodes-component-finder/
2. npm install
3. npm run build
4. Run n8n with the node mounted in (replace FULL_PATH_TO_REPO with your own path):

   docker run -it --rm --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n -v FULL_PATH_TO_REPO/n8n-nodes-component-finder:/home/node/.n8n/custom/n8n-nodes-component-finder docker.n8n.io/n8nio/n8n

5. Search "Component Finder Agent" when adding a node in n8n.

### Using it
1. Add the node to a workflow
2. Set up a credential with your Gemini API key and service URL (http://host.docker.internal:8000)
3. Fill in the Query field (e.g. "LM358 op-amp") and execute