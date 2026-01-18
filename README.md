# Personal Chatbot

A personal AI chatbot that answers questions in your voice using your LinkedIn PDF
and a short personal summary. It launches a Gradio chat UI and uses OpenAI models
to generate responses, with a lightweight evaluator step to check quality before
replying.

## What It Does

- Extracts text from a LinkedIn PDF and a summary file.
- Builds a system prompt that keeps the assistant in character.
- Generates replies via OpenAI and evaluates them before returning.
- Serves a simple web UI with Gradio.

## Project Files

- `personal_chatbot.py`: Main script that loads data, builds prompts, runs the
  evaluator loop, and starts the Gradio UI.
- `me/summary.txt`: Short personal summary used to ground responses.
- `me/linkedin.pdf`: LinkedIn PDF export used as source material.

## Requirements

Install dependencies with uv (recommended):

```
uv sync
```

Or with pip:

```
pip install python-dotenv openai pypdf gradio pydantic
```

## Setup

Ensure the following files exist in the `me/` folder next to
`personal_chatbot.py`:

- `me/linkedin.pdf`
- `me/summary.txt`

Set environment variables (for example in a `.env` file):

- `OPENAI_API_KEY` for OpenAI

## Run

```
python personal_chatbot.py
```

