# no-direct-bind

A property, a machine-checked proof that it holds, and a runnable witness you can attack.

This repository states one theorem about AI-agent execution, proves it over the entire
reachable state space, gives a formal (TLA+) specification of the same property, and ships
an executable witness plus an adversarial suite that tries to break it.

It is the canonical statement of the **No-Direct-Bind** property. Everything else is
support for the claim.

---

## Theorem 1 — No-Direct-Bind

> In any run of the gated architecture, the system reaches an `EXECUTED` state only via a
> transition guarded by `resolvedAllow = TRUE`.
> Equivalently: **there is no reachable state in which an effect has occurred while
> authority was unresolved.** Absence of a resolved ALLOW is `HOLD`, by construction —
> fail-closed.

Formally (TLA+ safety invariant):

```
NoDirectBind == (phase = "EXECUTED") => (resolvedAllow = TRUE)
```

## Why this is a theorem, not a demo

A demo shows that the gate works on the cases you thought of. This shows two stronger things:

1. **Universality.** `proof/model.py` enumerates *every* reachable state of a small agent
   model and confirms the invariant holds in all of them — not a sample, the whole space.
2. **Load-bearing.** The same file defines an *ungated* variant with a "direct bind"
   shortcut, and proves it **violates** the invariant, producing an explicit counterexample:

   ```
   EXECUTED with authority_present=False, resolved_allow=False
   ```

   So the gate is not decoration. Remove it and the property provably fails. That is the
   difference between "here is code that passes tests" and "here is a structure that must
   hold or must break."

## Verify it yourself

```bash
# 1. Exhaustive proof + falsifier (pure Python, no deps)
python proof/model.py
#   [gated]   No-Direct-Bind holds over all 13 reachable states: True
#   [ungated] direct-bind shortcut produces a violation: True

# 2. Adversarial suite — every attempt to bind without authority must fail
pip install pytest
python -m pytest adversarial/ -q          # 7 passed

# 3. Formal spec (optional, requires TLA+ / TLC)
#    Open spec/NoDirectBind.tla. Uncomment the `Direct` action and add it to
#    `Next` — TLC will then report NoDirectBind violated, confirming the
#    invariant is meaningful and the guard is what closes it.
```

## Layout

```
spec/NoDirectBind.tla     formal property + state machine (TLA+)
spec/NoDirectBind.cfg     TLC model-check config
proof/model.py            exhaustive reachable-state proof + counterexample
witness/                  ndb-gate: the executable witness (the proof made runnable)
adversarial/              falsification suite: attacks that must all fail
```

The witness (`witness/`) is the [ndb-gate](https://github.com/LalaSkye/ndb-gate) library:
a fail-closed gate where `bind()` is the sole path to an effect.

## Open challenge

The point of stating a falsifiable property is to be falsified if it is wrong.

**If you can construct an agent model that reaches an effect without a resolved ALLOW, and
the adversarial suite still passes, open an issue.** Break it, and you have found the limit
of the claim. That is the contribution either way.

## Claim discipline

- **PROVED:** the property holds over the modelled state space, and the ungated variant
  violates it. The tests and `model.py` demonstrate both.
- **PLAUSIBLE:** that this pattern generalises to production agent stacks. Stated, not proved.
- **NOT CLAIMED:** that this is a security product, or that it hardens any specific deployment.

## License

Apache-2.0.
