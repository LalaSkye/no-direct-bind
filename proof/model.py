"""Exhaustive state-model proof of the No-Direct-Bind theorem.

We model an agent as a small transition system and EXHAUSTIVELY enumerate every
reachable state. The theorem is then a property checked over the entire reachable
state space — not a sample, not a test fixture, but all of it.

THEOREM 1 (No-Direct-Bind).
    In any run of the gated architecture, the system reaches an EXECUTED state
    only via a transition whose guard is `resolved_allow == True`.
    Equivalently: there is NO reachable state in which an effect has occurred
    while authority was unresolved.

We prove it two ways:
    (A) Safety invariant holds in every reachable state (this file).
    (B) An "ungated" variant is shown to VIOLATE it — demonstrating the gate is
        load-bearing, not decorative (see counterexample()).
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from itertools import product


class Phase(Enum):
    IDLE = "IDLE"            # no intent yet
    INTENT = "INTENT"        # latent intent present, unresolved
    RESOLVED = "RESOLVED"    # authority check has run
    EXECUTED = "EXECUTED"    # terminal effect has occurred


@dataclass(frozen=True)
class State:
    phase: Phase
    authority_present: bool   # an authority token was supplied
    evidence_proved: bool     # evidence meets the PROVED bar
    resolved_allow: bool      # the gate resolved to ALLOW


def initial_states() -> list[State]:
    """All starting configurations of the environment we must be safe under."""
    states = []
    for auth, ev in product([False, True], repeat=2):
        states.append(State(Phase.IDLE, auth, ev, resolved_allow=False))
    return states


def gated_transitions(s: State) -> list[State]:
    """The gated architecture. The ONLY edge into EXECUTED is guarded by
    resolved_allow == True, which itself can only be set when authority is
    present AND evidence is PROVED."""
    out: list[State] = []

    if s.phase is Phase.IDLE:
        out.append(replace(s, phase=Phase.INTENT))           # an intent forms

    elif s.phase is Phase.INTENT:
        # Resolution step: the gate evaluates. ALLOW iff authority + proved evidence.
        allow = s.authority_present and s.evidence_proved
        out.append(replace(s, phase=Phase.RESOLVED, resolved_allow=allow))

    elif s.phase is Phase.RESOLVED:
        if s.resolved_allow:                                  # guarded edge
            out.append(replace(s, phase=Phase.EXECUTED))
        # if not allowed: no successor into EXECUTED. Fail-closed: it simply halts.

    # EXECUTED is terminal.
    return out


def ungated_transitions(s: State) -> list[State]:
    """A DELIBERATELY broken variant with a 'direct bind' shortcut: intent can
    jump straight to EXECUTED. Used to show the theorem is falsifiable and that
    the gate is what makes it hold."""
    out = gated_transitions(s)
    if s.phase is Phase.INTENT:
        out.append(replace(s, phase=Phase.EXECUTED))          # the forbidden shortcut
    return out


def safety_invariant(s: State) -> bool:
    """No-Direct-Bind as a state predicate:
        if executed, then authority was resolved to ALLOW.
    """
    if s.phase is Phase.EXECUTED:
        return s.resolved_allow is True
    return True


def reachable(transition_fn) -> set[State]:
    """Exhaustive BFS over the entire reachable state space."""
    frontier = list(initial_states())
    seen: set[State] = set(frontier)
    while frontier:
        s = frontier.pop()
        for nxt in transition_fn(s):
            if nxt not in seen:
                seen.add(nxt)
                frontier.append(nxt)
    return seen


def check(transition_fn) -> tuple[bool, State | None, int]:
    """Returns (holds, first_violation_or_None, num_states_checked)."""
    states = reachable(transition_fn)
    for s in states:
        if not safety_invariant(s):
            return (False, s, len(states))
    return (True, None, len(states))


def counterexample() -> State | None:
    """The ungated architecture must violate the invariant. If it does not,
    our model is too weak to be meaningful."""
    holds, violation, _ = check(ungated_transitions)
    return None if holds else violation


if __name__ == "__main__":
    ok, _, n = check(gated_transitions)
    print(f"[gated]   No-Direct-Bind holds over all {n} reachable states: {ok}")

    bad = counterexample()
    print(f"[ungated] direct-bind shortcut produces a violation: {bad is not None}")
    if bad:
        print(f"          witness violation state: {bad}")
