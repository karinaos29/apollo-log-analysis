"""
Small Ollama chat client shared by the generation pipelines.

Decoding settings are fixed so runs are comparable: low temperature, a seed,
an explicit context window (so prompts are never silently truncated) and a cap
on output length. Pass a different `seed` to get a different sample of the same
prompt (used for repeat runs).
"""
import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_SEED = 42
OPTIONS = {"temperature": 0.3, "top_p": 0.9, "seed": DEFAULT_SEED, "num_ctx": 4096, "num_predict": 600}

RETRY_TEMPLATE = """That draft breaks these rules:
{problems}
Rewrite the whole {part} part so it follows all of them. Output only the rewritten text."""


def chat(messages: list, model: str, seed: int = None):
    """Returns (text, prompt_tokens, was_cut_off_by_length_limit)."""
    options = dict(OPTIONS, seed=DEFAULT_SEED if seed is None else seed)
    resp = requests.post(
        OLLAMA_URL,
        json={"model": model, "messages": messages, "stream": False, "options": options},
        timeout=900,
    )
    resp.raise_for_status()
    body = resp.json()
    return body["message"]["content"].strip(), body.get("prompt_eval_count", 0), body.get("done_reason") == "length"


def unload(model: str):
    """Ask Ollama to free the model's memory (matters on an 8 GB machine)."""
    try:
        requests.post(OLLAMA_URL, json={"model": model, "keep_alive": 0}, timeout=30)
    except requests.RequestException:
        pass
