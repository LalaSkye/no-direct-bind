"""The No-Direct-Bind gate.

WITNESS PROPERTY (model-local No-Direct-Bind):
    An unresolved latent intent cannot bind to a terminal action.
    bind(intent) -> effect  IFF  resolve(authority, evidence) == ALLOW.
    Otherwise the outcome is HOLD (fail-closed) or DENY. Never silent execution.

Within this witness, the gate is the only path to the supplied effect function.
That is not a claim about any caller's other code paths.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum
from typing import Callable

from .authority import AuthorityToken, EvidenceClass
from .receipts import ReceiptChain, Receipt


class Outcome(Enum):
    ALLOW = "ALLOW"
    HOLD = "HOLD"
    DENY = "DENY"


@dataclass(frozen=True)
class Decision:
    outcome: Outcome
    reason: str
    receipt: Receipt
    effect: object | None = None  # populated ONLY on ALLOW


class Gate:
    """Fail-closed execution gate.

    `required` is the minimum evidence class needed to authorise. Default PROVED:
    nothing weaker than first-party, verified evidence can bind a terminal action.
    """

    def __init__(self, required: EvidenceClass = EvidenceClass.PROVED) -> None:
        self.required = required
        self.chain = ReceiptChain()
        self._spent_tokens: set[int] = set()

    def bind(
        self,
        action: str,
        scope: str,
        token: AuthorityToken | None,
        effect_fn: Callable[[], object],
        now: float | None = None,
    ) -> Decision:
        """Attempt to bind `action` in `scope` to its terminal effect.

        The effect_fn is invoked IF AND ONLY IF the decision resolves to ALLOW.
        Every call emits a receipt regardless of outcome.
        """
        now = time.time() if now is None else now

        def _record(outcome: Outcome, reason: str, ev: str) -> Decision:
            receipt = self.chain.append(action, scope, outcome.value, reason, ev)
            effect = None
            if outcome is Outcome.ALLOW:
                effect = effect_fn()  # the ONLY place an effect is ever produced
            return Decision(outcome=outcome, reason=reason, receipt=receipt, effect=effect)

        # --- Fail-closed checks, strongest reason first ---

        if token is None:
            return _record(Outcome.HOLD, "no authority token presented", "NOT_ADMISSIBLE")

        if not token.evidence.evidence_class.is_admissible:
            return _record(Outcome.DENY, "evidence not admissible", token.evidence.evidence_class.value)

        if not token.covers(action, scope):
            return _record(
                Outcome.DENY,
                f"token does not cover ({action!r},{scope!r}); no scope widening",
                token.evidence.evidence_class.value,
            )

        if not token.is_live(now):
            return _record(Outcome.HOLD, "authority expired", token.evidence.evidence_class.value)

        if token.single_use and id(token) in self._spent_tokens:
            return _record(
                Outcome.DENY,
                "single-use authority already spent; batch authority does not carry",
                token.evidence.evidence_class.value,
            )

        if not token.evidence.satisfies(self.required):
            return _record(
                Outcome.HOLD,
                f"evidence {token.evidence.evidence_class.value} below required {self.required.value}",
                token.evidence.evidence_class.value,
            )

        # All checks passed -> the unique ALLOW path.
        if token.single_use:
            self._spent_tokens.add(id(token))
        return _record(Outcome.ALLOW, "evidenced authority resolved", token.evidence.evidence_class.value)
