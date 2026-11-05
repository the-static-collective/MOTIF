"""MOTIF-023F: real FLAN-T5 critic with a *token-level* registered-ID gate.

This does not reconstruct arbitrary prose or use a keyword classifier as if
it were model intelligence. The tokenizer's EXACT token sequences for
registered actions are the only outputs that can be generated. The real
language model chooses between them by its next-token scores. NO_TEST is a
safe explicit abstention; it does not authorize or dispatch anything.

Other two Chorus roles are scripted for the *multi-case* measurement to keep
cost low. A separate full-Chorus experiment runs all three with real T5.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import re
import threading
import time

from chorus import LocalFlanT5Small, PublicProjection


NO_TEST = "NO_TEST"


@dataclass(frozen=True)
class ChoiceReport:
    selected: str
    raw: str
    method: str
    prompt_chars: int
    elapsed_seconds: float
    accepted_decoder_tokens: bool
    model_inference: bool = True


def permitted_sequences(tokenizer, ids: tuple[str, ...], *, allow_abstain: bool = True):
    """Build strictly finite acceptable output space at token granularity."""
    if len(ids) != len(set(ids)) or len(ids) > 8:
        raise ValueError("HOLD_DUPLICATE_OR_TOO_MANY_CHOICES")
    names = tuple(ids) + ((NO_TEST,) if allow_abstain else ())
    if any(not re.fullmatch(r"[A-Z][A-Z0-9_]{0,39}", s) for s in names):
        raise ValueError("HOLD_UNSAFE_TEST_ID")
    eos = tokenizer.eos_token_id
    if not isinstance(eos, int):
        raise ValueError("HOLD_MISSING_TOKENIZER_EOS")
    seqs = {}
    for name in names:
        text = "TEST_ID=" + name
        tokens = tuple(tokenizer.encode(text, add_special_tokens=False)) + (eos,)
        if tokens in seqs:
            raise ValueError("HOLD_TOKENIZER_CHOICE_COLLISION")
        seqs[tokens] = text
    return seqs


def allowed_next(prefix: tuple[int, ...], seqs: dict[tuple[int, ...], str], eos: int) -> list[int]:
    """Only allow next tokens from the exact registered decision trie."""
    found = sorted({
        key[len(prefix)] for key in seqs
        if len(key) > len(prefix) and key[:len(prefix)] == prefix
    })
    return found or [eos]


class RealT5Critic:
    """The model is REAL; optional observer/hypeman stand-ins are NOT."""

    def __init__(self, model: LocalFlanT5Small,
                 projection: PublicProjection,
                 test_labels: tuple[tuple[str, str], ...],
                 *,
                 method: str = "CONSTRAINED_IDS"):
        if method not in {"CONSTRAINED_IDS", "CONSTRAINED_ID_ONLY", "RAW_GENERATION"}:
            raise ValueError("HOLD_BAD_MODEL_METHOD")
        self.inner = model
        self.projection = projection
        self.test_labels = tuple(test_labels)
        self.ids = tuple(c[0] for c in test_labels)
        if len(self.ids) > 7 or len(set(self.ids)) != len(self.ids):
            raise ValueError("HOLD_BAD_CATALOG")
        self.method = method
        self.name = "REAL_FLAN_T5_SMALL_" + method
        self.critic_calls = 0
        self.reports: list[ChoiceReport] = []
        self._lock = threading.Lock()

    def _prompt(self) -> str:
        catalog = "\n".join(s + " : " + label for s, label in self.test_labels)
        abstain = self.method != "CONSTRAINED_ID_ONLY"
        return (
            "Choose the most useful NEW missing question for this imaginary "
            "planning task. Return one registered ID only. "
            "Do not answer the question or authorize action. "
            + ("If none is useful, choose NO_TEST. " if abstain else
               "The native verifier will reject any incorrect or redundant choice. ") + "\n"
            "KNOWN: " + "; ".join(self.projection.facts) + "\n"
            "UNKNOWN: " + "; ".join(self.projection.uncertainties) + "\n"
            "CURRENT NEXT: " + self.projection.proposed_next + "\n"
            "TESTS:\n" + catalog +
            ("\nABSTAIN: NO_TEST\n" if abstain else "\n")
            + "Reply strictly as TEST_ID=<name>.\n"
        )

    def generate(self, prompt: str) -> str:
        if not (prompt.startswith("ROLE=CRITIC.")
                or prompt.startswith("Return EXACTLY TEST_ID=")):
            # Honest fixtures, not two secretly model-written outputs.
            if prompt.startswith("ROLE=OBSERVER."):
                return "SCRIPTED: Known facts and uncertainties were recorded separately."
            if prompt.startswith("ROLE=HYPEMAN."):
                return "SCRIPTED: Preserve the smallest useful reversible step."
            raise ValueError("HOLD_UNRECOGNIZED_ROLE")
        with self._lock:
            self.critic_calls += 1
            began = time.monotonic()
            if self.method == "RAW_GENERATION":
                # Use *unmodified* 022F QuestionAwareBackend prompt; measures
                # true unconstrained small-model format failure.
                raw = self.inner.generate(prompt)
                text = raw
                accepted = bool(re.fullmatch(
                    r"TEST_ID=[A-Z][A-Z0-9_]{0,39}", raw.strip()
                ))
                prompt_chars = len(prompt)
            else:
                import torch
                self.inner._prepare()
                tokenizer = self.inner._tokenizer
                model = self.inner._model
                seqs = permitted_sequences(
                    tokenizer, self.ids,
                    allow_abstain=self.method != "CONSTRAINED_ID_ONLY",
                )
                p = self._prompt()
                input_tensor = tokenizer(
                    p, return_tensors="pt", max_length=384, truncation=True,
                )
                eos = tokenizer.eos_token_id
                start = model.config.decoder_start_token_id
                if not isinstance(start, int):
                    raise ValueError("HOLD_UNKNOWN_DECODER_START")
                def allowed(_batch_id, output_ids):
                    tokens = tuple(output_ids.tolist())
                    if tokens and tokens[0] == start:
                        tokens = tokens[1:]
                    return allowed_next(tokens, seqs, eos)
                with torch.inference_mode():
                    out = model.generate(
                        **input_tensor, num_beams=2, do_sample=False,
                        prefix_allowed_tokens_fn=allowed,
                        max_new_tokens=max(len(x) for x in seqs)+2,
                        early_stopping=True,
                    )
                observed = tuple(out[0].tolist())
                if observed and observed[0] == start:
                    observed = observed[1:]
                if observed not in seqs:
                    raise ValueError("HOLD_OUT_OF_TRIE_GENERATION")
                raw = tokenizer.decode(out[0], skip_special_tokens=True)
                # These canonical IDs come only from exact decoder token
                # sequences, not fuzzy repair of hallucinated text.
                text = seqs[observed]
                accepted = True
                prompt_chars = len(p)
            self.reports.append(ChoiceReport(
                selected=text, raw=raw, method=self.method,
                prompt_chars=prompt_chars,
                elapsed_seconds=round(time.monotonic()-began,3),
                accepted_decoder_tokens=accepted,
            ))
            return text
