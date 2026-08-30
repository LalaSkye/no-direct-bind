"""ndb-gate — small executable witness for No-Direct-Bind.

Witness property (model-local No-Direct-Bind):
    An unresolved latent intent cannot bind to a terminal action.
    Binding occurs IF AND ONLY IF an evidenced authority check resolves to ALLOW.
    Absence of a resolved ALLOW yields HOLD (fail-closed), never execution.

This package is a minimal reference witness. The property holds because this
witness exposes one path to its local effect function. It does not establish
non-bypassability in an external application or agent stack.
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
