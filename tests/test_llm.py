import numpy as np
import types

import pytest

from llm import LLMResponder


class FakeTokenizer:
    def __call__(self, prompt, return_tensors=None, truncation=None, max_length=None):
        # return a simple object with input_ids that has a shape attribute
        arr = np.array([[1, 2, 3]])
        return {"input_ids": arr}

    def decode(self, ids, skip_special_tokens=True):
        return "This is a test answer. [sample_doc_1.txt]"


class FakeModel:
    def generate(self, **kwargs):
        # Return something that behaves like token ids
        return np.array([[1, 2, 3]])


def make_fake_responder():
    # Create object without calling heavy __init__
    responder = object.__new__(LLMResponder)
    responder.tokenizer = FakeTokenizer()
    responder.model = FakeModel()
    responder.device = None
    responder.openai_enabled = False
    return responder


def test_make_prompt_includes_question_and_context():
    r = make_fake_responder()
    # Reuse real make_prompt implementation
    # craft fake results
    results = [{"metadata": {"source_file": "sample_doc_1.txt"}, "document": "Test content about time off."}]
    prompt = LLMResponder.make_prompt(r, "How do I request time off?", results)
    assert "Question:" in prompt
    assert "sample_doc_1.txt" in prompt


def test_generate_returns_decoded_text():
    r = make_fake_responder()
    out = LLMResponder.generate(r, "How do I request time off?", [{"metadata": {"source_file": "sample_doc_1.txt"}, "document": "Test."}], max_new_tokens=10)
    assert isinstance(out, str)
    assert "sample_doc_1.txt" in out or "test answer" in out.lower()
