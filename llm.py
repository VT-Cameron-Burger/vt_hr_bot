"""Simple LLM wrapper using Hugging Face transformers.

This wrapper uses an instruction-tuned text2text model (default:
`google/flan-t5-small`) to synthesize answers from retrieved document
chunks. It's suitable for local development; for production you may
prefer a hosted or larger instruction model.
"""

from typing import List, Dict, Optional
import os
try:
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    import torch
except Exception:
    AutoTokenizer = None
    AutoModelForSeq2SeqLM = None
    torch = None

# Optional OpenAI fallback (used only if OPENAI_API_KEY is set and `openai`
# package is installed). This is a non-default path and won't be used in
# unit tests unless the environment opts in.
try:
    import openai
except Exception:
    openai = None


class LLMResponder:
    """Seq2Seq responder using an instruction-tuned model like flan-t5-small.

    This implementation loads tokenizer + model and calls model.generate()
    directly which avoids pipeline incompatibilities on some environments.
    """

    def __init__(self, model_name: str = "google/flan-t5-small", device=None):
        if AutoTokenizer is None or AutoModelForSeq2SeqLM is None:
            raise ImportError("transformers (AutoTokenizer/AutoModelForSeq2SeqLM) are required for LLMResponder")

        self.model_name = model_name
        # Choose device: prefer provided device, otherwise prefer mps on mac, then cpu
        self.device = device
        if self.device is None and torch is not None:
            if getattr(torch.backends, 'mps', None) is not None and torch.backends.mps.is_available():
                self.device = torch.device('mps')
            else:
                self.device = torch.device('cpu')

    # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
        if self.device is not None:
            try:
                self.model.to(self.device)
            except Exception:
                # ignore device move errors
                pass

        # Check for OpenAI fallback availability
        self.openai_enabled = False
        self.openai_model = os.environ.get('OPENAI_FALLBACK_MODEL', 'gpt-3.5-turbo')
        if os.getenv('OPENAI_API_KEY') and openai is not None:
            try:
                openai.api_key = os.getenv('OPENAI_API_KEY')
                self.openai = openai
                self.openai_enabled = True
            except Exception:
                # don't enable fallback if there's any import/config issue
                self.openai_enabled = False

    def make_prompt(self, query: str, results: List[Dict]) -> str:
        ctxts = []
        for r in results:
            src = r.get("metadata", {}).get("source_file", "unknown")
            preview = r.get("document", "").strip().replace("\n", " ")
            preview = preview[:512]
            ctxts.append(f"Source: {src}\n{preview}")

        context = "\n\n".join(ctxts)
        # Strong prompt that instructs the model to answer only from the
        # provided context and to include explicit citations in square
        # brackets (e.g., [sample_doc_1.txt]) for any facts it mentions.
        prompt = (
            "You are an assistant that answers HR questions using ONLY the provided context. "
            "Do not invent facts. If the answer cannot be determined from the context, reply:\n"
            '"I do not know — please contact HR or consult the provided documents."\n\n'
            "When you provide facts, include the source filename in square brackets after the fact.\n\n"
            f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:")
        return prompt

    def generate(
        self,
        query: str,
        results: List[Dict],
        max_new_tokens: int = 128,
        do_sample: bool = False,
        temperature: float = 0.0,
        top_p: float = 0.95,
        num_beams: int = 1,
        request_id: Optional[str] = None,
    ) -> str:
        """Generate an answer from the model.

        Uses max_length computed from input length + max_new_tokens to be
        compatible with transformers versions that don't support
        `max_new_tokens`.

        Parameters returned to model.generate are configurable to allow
        quick experimentation (deterministic or sampled outputs).
        """

        prompt = self.make_prompt(query, results)
        # Prepare tokenizer/model inputs for local generation
        inputs = self.tokenizer(prompt, return_tensors='pt', truncation=True, max_length=1024)
        if self.device is not None and torch is not None:
            try:
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
            except Exception:
                pass

        # Compute max_length for compatibility
        input_len = inputs['input_ids'].shape[1]
        max_length = input_len + max_new_tokens

        gen_kwargs = {
            "max_length": max_length,
            "do_sample": do_sample,
            "temperature": float(temperature),
        }
        # Only include top_p if sampling
        if do_sample:
            gen_kwargs["top_p"] = float(top_p)
        # If user requests beam search
        if num_beams and num_beams > 1:
            gen_kwargs["num_beams"] = int(num_beams)

        try:
            gen_ids = self.model.generate(**inputs, **gen_kwargs)
            gen = self.tokenizer.decode(gen_ids[0], skip_special_tokens=True)
            gen = " ".join(gen.split())
            return gen
        except Exception as e:
            # If local generation fails and OpenAI fallback is enabled, use it
            if self.openai_enabled:
                try:
                    return self._call_openai_fallback(prompt, max_new_tokens, temperature=float(temperature), request_id=request_id)
                except Exception:
                    pass
            # Re-raise original exception if no fallback
            raise

    def _call_openai_fallback(self, prompt: str, max_new_tokens: int = 128, temperature: float = 0.0, request_id: Optional[str] = None) -> str:
        """Call OpenAI ChatCompletion as a fallback. Returns the assistant text.

        This is only used when `OPENAI_API_KEY` is set in the environment and
        the `openai` package is installed. It uses the chat completion API.
        """
        if not self.openai_enabled:
            raise RuntimeError("OpenAI fallback not enabled")

        # Build messages for chat completion
        messages = [
            {"role": "system", "content": "You are an assistant that answers only from provided context and includes source citations in square brackets."},
            {"role": "user", "content": prompt}
        ]

        resp = self.openai.ChatCompletion.create(
            model=self.openai_model,
            messages=messages,
            temperature=temperature,
            max_tokens=int(max_new_tokens),
            n=1,
        )

        # Log usage if available for local cost tracking
        try:
            usage = resp.get('usage') if isinstance(resp, dict) else None
            if usage:
                log_entry = {
                    'timestamp': __import__('datetime').datetime.utcnow().isoformat() + 'Z',
                    'request_id': request_id,
                    'model': self.openai_model,
                    'requested_max_tokens': int(max_new_tokens),
                    'usage': usage,
                }
                log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'openai_usage.log')
                try:
                    with open(log_path, 'a', encoding='utf-8') as lf:
                        lf.write(__import__('json').dumps(log_entry) + '\n')
                except Exception:
                    # If logging fails, don't break the response
                    pass
        except Exception:
            # ignore logging errors
            pass

        # Extract assistant content
        try:
            return resp['choices'][0]['message']['content'].strip()
        except Exception:
            # fallback to plain text extraction if format differs
            return str(resp)

