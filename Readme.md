# My Desktop AI Agent

I've been experimenting with LLMs and wanted to build something more practical than just chatting with them.

So I started building this little desktop AI agent using Python. The idea is simple: give an LLM access to a set of tools so it can interact with my filesystem, search the web, and perform a few basic tasks on my computer.

Im currently using **Groq API** and **Ollama**, so I can experiment with both cloud-based and locally running models.

This is still a work in progress, and Im continuously trying to improve its architecture, reliability, and capabilities.

## What can it do currently?

Here's what I've implemented so far:

**Filesystem**
- Create files.
- Read files (in chunks).
- Append content to files.
- Edit existing files.
- Move and rename files/folders.
- List directory contents.
- Search for files by name.
- Search for specific text inside files.

**Other tools**
- Search the web using DuckDuckGo.
- Open configured desktop applications.
- Get the current date and time.
- Ask me questions when it needs additional information.

All filesystem operations are restricted to a dedicated `workspace/` directory.

## How it works

I wanted to understand how tool-using agents work, so I built the basic agent loop myself.

The model receives a system prompt containing the available tools and their arguments. Based on the user's request, it either makes a tool call or returns a final response.

Tool calls are returned as JSON, which I parse and validate before executing the corresponding Python function.

The result is then sent back to the model, allowing it to decide what to do next.

The process continues until it produces a final answer or reaches the maximum number of steps.

```text
User
  |
  v
Agent Loop
  |
  v
LLM (Groq / Ollama)
  |
  v
JSON Response
  |
  v
Parser & Validation
  |
  v
Tool Execution
  |
  v
Tool Result
  |
  +------> Back to LLM
```

## Tech Stack

- **Python** — Main language.
- **Groq** — API-based inference.
- **Ollama** — Local model inference.
- **DuckDuckGo Search** — Web search.
- **Pathlib / OS / Shutil** — Filesystem operations.
- **Subprocess** — Launching desktop applications.

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/desktop-agent.git
cd desktop-agent
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

For Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Groq (optional)

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_api_key
```

This is only needed when using the Groq API.

### 5. Choose your model

In `response.py`, select the inference mode:

```python
MODE = "api"
```

For local inference:

```python
MODE = "local"
```

Make sure Ollama is running and the model specified in `MODEL` is installed.

### 6. Run

```bash
python agent.py
```

## Current Limitations

There are still quite a few things I want to improve:

- The agent relies on a JSON-based tool-calling format.
- It has a fixed maximum number of execution steps.
- Conversation history is currently maintained in memory.
- Available applications have to be configured manually.
- Local model performance depends heavily on the model and available hardware.
- The interface is currently just a terminal.
- Error handling and tool execution reliability still need work.

## Things I Want to Work On

Some things I'd like to experiment with next:

- Improving the agent loop and overall architecture.
- Making tool registration and management cleaner.
- Better conversation management and persistent memory.
- Adding terminal command execution.
- Adding tools specifically for working with code.
- Improving the terminal interface.
- Making tool execution safer and more reliable.

## Why I Built This

Mostly because I wanted to understand how LLMs can interact with the environment around them instead of just generating text.

Building this has been a good way to experiment with tool calling, prompting, local inference, API integration, and designing a small agent architecture.

There's still a lot to learn and improve, but that's the point.

**More experiments and improvements coming!**