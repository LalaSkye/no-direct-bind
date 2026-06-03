"""ndb-gate — No-Direct-Bind execution gate for AI agents.

Core property (Theorem 1, No-Direct-Bind):
    An unresolved latent intent cannot bind to a terminal action.
    Binding occurs IF AND ONLY IF an evidenced authority check resolves to ALLOW.
    Absence of a resolved ALLOW yields HOLD (fail-closed), never execution.

This package is a minimal, runnable reference implementation. It is deliberately
small: the point is that the property is enforced by construction and is testable,
not that the library is large.
"""

from .gate import Gate, Decision, Outcome
from .authority import AuthorityToken, Evidence, EvidenceClass
from .receipts import Receipt, ReceiptChain, verify_chain

__all__ = [
    "Gate",
    "Decision",
    "Outcome",
    "AuthorityToken",
    "Evidence",
    "EvidenceClass",
    "Receipt",
    "ReceiptChain",
    "verify_chain",
]

__version__ = "0.1.0"
