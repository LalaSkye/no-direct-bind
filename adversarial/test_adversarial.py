"""Adversarial falsification suite.

These are not gentle unit tests. Each one is an ATTEMPT to reach an effect
without a resolved ALLOW — i.e. to break the No-Direct-Bind theorem. Every
attempt must FAIL to execute. If any succeeds, the theorem is false and the
suite goes red.

Two layers:
  1. Against the formal model (proof/model.py) — exhaustive.
  2. Against the executable witness (witness ndb_gate) — concrete API.
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(ROOT, "proof"))
sys.path.insert(0, os.path.join(ROOT, "witness", "src"))

import pytest

from model import check, gated_transitions, ungated_transitions, counterexample, Phase
from ndb_gate import Gate, Outcome, AuthorityToken, Evidence, EvidenceClass


# ---- Layer 1: the model -----------------------------------------------------

def test_theorem_holds_over_entire_reachable_space():
    holds, violation, n = check(gated_transitions)
    assert holds is True, f"violation in reachable space: {violation}"
    assert n > 0


def test_ungated_architecture_is_provably_broken():
    # The falsifier MUST produce a counterexample, else the model is vacuous.
    bad = counterexample()
    assert bad is not None
    assert bad.phase is Phase.EXECUTED
    assert bad.resolved_allow is False   # executed without resolved authority


# ---- Layer 2: the executable witness ---------------------------------------

EFFECT_SINK = []
def effect():
    EFFECT_SINK.append("FIRED")
    return "FIRED"


def setup_function():
    EFFECT_SINK.clear()


def test_attack_no_token():
    g = Gate()
    d = g.bind("x", "s", None, effect)
    assert d.outcome is Outcome.HOLD and EFFECT_SINK == []


def test_attack_forged_weak_evidence():
    g = Gate()
    tok = AuthorityToken("x", "s", Evidence("forged", EvidenceClass.PATTERN_ONLY, "fake"))
    d = g.bind("x", "s", tok, effect)
    assert d.outcome is Outcome.HOLD and EFFECT_SINK == []


def test_attack_scope_smuggling():
    # token for a low-stakes scope, used to try to execute in a high-stakes one
    g = Gate()
    tok = AuthorityToken("x", "sandbox", Evidence("ok", EvidenceClass.PROVED, "first-party"))
    d = g.bind("x", "prod", tok, effect)
    assert d.outcome is Outcome.DENY and EFFECT_SINK == []


def test_attack_token_replay():
    g = Gate()
    tok = AuthorityToken("x", "s", Evidence("ok", EvidenceClass.PROVED, "first-party"))
    g.bind("x", "s", tok, effect)            # legitimate first use
    d2 = g.bind("x", "s", tok, effect)       # replay attack
    assert d2.outcome is Outcome.DENY and EFFECT_SINK == ["FIRED"]  # only once


def test_only_proved_authority_ever_fires():
    g = Gate()
    tok = AuthorityToken("x", "s", Evidence("ok", EvidenceClass.PROVED, "first-party"))
    d = g.bind("x", "s", tok, effect)
    assert d.outcome is Outcome.ALLOW and EFFECT_SINK == ["FIRED"]
