#!/usr/bin/env python3
"""Test the OpenAI fallback path for LLMResponder.

This script is safe and opt-in: it will only call OpenAI if OPENAI_API_KEY
is set in the environment and the `openai` package is available in the
active Python environment. Use it like:

  source .venv/bin/activate
  export OPENAI_API_KEY="sk-..."
  python scripts/test_openai_fallback.py

It prints the prompt (truncated) and the OpenAI assistant response.
"""
import os
import sys

# Ensure repo root is importable when running from scripts/
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    from llm import LLMResponder
except Exception as e:
    print(f"Failed to import LLMResponder: {e}")
    sys.exit(2)


def main():
    # Instantiate responder (it will enable OpenAI fallback only if the
    # environment and package are present)
    responder = None
    try:
        responder = LLMResponder(model_name="google/flan-t5-small", device=None)
    except Exception as e:
        print(f"Warning: could not fully initialize local model: {e}\nProceeding to test OpenAI fallback only if available.")
        # Try to create a minimal responder object with openai fallback flag
        try:
            responder = object.__new__(LLMResponder)
            responder.openai_enabled = False
            # attempt to set attribute if available in module
            if hasattr(LLMResponder, 'openai_enabled'):
                responder.openai_enabled = getattr(LLMResponder, 'openai_enabled', False)
        except Exception:
            pass

    # Check if OpenAI fallback is enabled
    if not getattr(responder, 'openai_enabled', False):
        print("OpenAI fallback is not enabled.")
        print("Make sure you have installed the openai package in the active venv and exported OPENAI_API_KEY in this shell.")
        print("Example:\n  source .venv/bin/activate\n  pip install openai\n  export OPENAI_API_KEY=\"sk-...\"")
        sys.exit(1)

    # Build a small example context
    results = [{
        "metadata": {"source_file": "sample_doc_1.txt"},
        "document": "Vacation policy: Submit requests through the HR portal at least 2 weeks before planned leave. Managers must approve requests in the system."
    }]

    # Create prompt and call the fallback
    prompt = responder.make_prompt("How do I request time off?", results)
    print("\n--- Prompt (truncated) ---\n")
    print(prompt[:1200])
    print("\nCalling OpenAI fallback (this will use your API key and may incur costs)...\n")

    try:
        out = responder._call_openai_fallback(prompt, max_new_tokens=150, temperature=0.2)
        print("\n--- OpenAI response ---\n")
        print(out)
    except Exception as e:
        print(f"OpenAI fallback call failed: {e}")
        sys.exit(3)


if __name__ == '__main__':
    main()
