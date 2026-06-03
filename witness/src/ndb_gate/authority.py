"""Authority and evidence primitives.

These encode the user's claim discipline directly:
    PROVED / PLAUSIBLE / PATTERN_ONLY / NOT_ADMISSIBLE

Only PROVED (direct, first-party) evidence can satisfy a strict authority check.
Everything weaker is, by construction, insufficient to authorise a terminal action.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class EvidenceClass(Enum):
    """Evidence classes, strongest first. Mirrors the user's claim ledger."""

    PROVED = "PROVED"                  # direct / first-party / verified
    PLAUSIBLE = "PLAUSIBLE"            # reasonable, unconfirmed
    PATTERN_ONLY = "PATTERN_ONLY"     # resemblance, not evidence
    NOT_ADMISSIBLE = "NOT_ADMISSIBLE"  # unsupported or unsafe

    @property
    def is_admissible(self) -> bool:
        return self is not EvidenceClass.NOT_ADMISSIBLE


@dataclass(frozen=True)
class Evidence:
    """A single piece of evidence backing an authority claim."""

    claim: str
    evidence_class: EvidenceClass
    source: str  # who/what attests to this, with provenance

    def satisfies(self, required: EvidenceClass) -> bool:
        """True iff this evidence is at least as strong as `required`.

        Ordering: PROVED > PLAUSIBLE > PATTERN_ONLY > NOT_ADMISSIBLE.
        """
        order = {
            EvidenceClass.PROVED: 3,
            EvidenceClass.PLAUSIBLE: 2,
            EvidenceClass.PATTERN_ONLY: 1,
            EvidenceClass.NOT_ADMISSIBLE: 0,
        }
        return order[self.evidence_class] >= order[required]


@dataclass(frozen=True)
class AuthorityToken:
    """An explicit, scoped, time-bounded grant of authority.

    Key design choices that enforce the user's invariants:
      * scope is explicit and bounded  -> no silent scope upgrade
      * single_use is True by default  -> batch authority does not carry over
      * expires_at bounds the grant     -> no open-ended authority
    """

    action: str
    scope: str
    evidence: Evidence
    issued_at: float = field(default_factory=time.time)
    ttl_seconds: float = 300.0
    single_use: bool = True

    @property
    def expires_at(self) -> float:
        return self.issued_at + self.ttl_seconds

    def is_live(self, now: float | None = None) -> bool:
        now = time.time() if now is None else now
        return now <= self.expires_at

    def covers(self, action: str, scope: str) -> bool:
        """Authority must match the exact action and scope. No widening."""
        return self.action == action and self.scope == scope
