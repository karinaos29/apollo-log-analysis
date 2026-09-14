# Local Foundation Model Shortlist

**Constraint:** Apple Silicon Mac, 8 GB unified memory. This memory is shared
between macOS, apps, and the model — realistically only ~5-6 GB is available
for the model itself. This rules out most 7B+ models comfortably, and makes
**context window** (how much of the JSON log fits in one prompt) as important
as raw quality, since a full simulation log can run to hundreds of lines.

All of these run via **Ollama** (`https://ollama.com`), which handles
Apple Silicon acceleration (Metal) automatically and uses 4-bit quantization
by default — the standard way to run local LLMs on a Mac without touching
CUDA/GPU code yourself.

## Primary candidates (comfortable fit)

| Model | Size | Context window | Why it's a good fit |
|---|---|---|---|
| **Phi-3.5-mini-instruct** | 3.8B | 128K tokens | Best context window in this size class — can likely fit a full JSON log in one prompt with room for the multi-step analysis. Strong instruction-following for its size. `ollama pull phi3.5` |
| **Qwen2.5 3B-instruct** | 3B | 32K tokens | Very strong for its size on structured-data reasoning and JSON specifically; multilingual (relevant since the platform needs French too). `ollama pull qwen2.5:3b` |
| **Llama 3.2 3B-instruct** | 3B | 128K tokens | Meta's latest small model, good general instruction-following, large context. `ollama pull llama3.2` |

## Stretch candidates (test if the above run smoothly with headroom to spare)

| Model | Size | Context window | Note |
|---|---|---|---|
| **Qwen2.5 7B-instruct** | 7B | 32K–128K (extended) | Noticeably stronger reasoning than the 3B tier; will be slow and memory-tight on 8GB — worth trying but expect to fall back if it swaps/crashes |
| **Llama 3.1 8B-instruct** | 8B | 128K | Same trade-off as above; industry-standard baseline worth having in the comparison if it runs at all |

## Setup (one-time)

```bash
brew install ollama          
ollama serve                 # runs the local server (localhost:11434)
ollama pull phi3.5
ollama pull qwen2.5:3b
ollama pull llama3.2
```
