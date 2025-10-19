# MOONLACE

Tiny CLI that chats *locally* with your STELLARWIND export using **Ollama** (ChatGPT optional later).

## Quickstart

```bash
ollama serve &
source .venv/bin/activate.fish
pip install -r requirements.txt
cp .env.example .env
# edit .env if needed
python moonlace.py -p ollama -d 2025-10-18 -q "Give me 3 bullets from RECENT.md and one next action."
