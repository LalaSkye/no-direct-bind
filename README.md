# no-direct-bind — model-local safety invariant

This repository contains a 13-state abstract model, a TLA+ specification and a
small executable witness for one safety property.

It proves the property only over the declared modelled state space and tests
it only against the supplied witness. It does not prove a theorem about AI
agents generally, LangChain, Kubernetes controllers or any external stack.

## Model property

> In any run of this gated model, `EXECUTED` is reachable only after
> `resolvedAllow = TRUE`.

Formally:

```text
NoDirectBind == (phase = "EXECUTED") => (resolvedAllow = TRUE)
```

This property holds because the model defines the only edge into `EXECUTED` as
guarded by `resolvedAllow`. The result is useful and falsifiable inside that
declared topology; it is not evidence that an unmodelled route cannot exist in
another system.

## Evidence supplied

1. **Exhaustive Python model check.** `proof/model.py` enumerates all 13
   reachable states of the small declared model and checks the invariant in
   each one.
2. **Model-local falsifier.** The same file adds a deliberately ungated
   `INTENT -> EXECUTED` transition and returns a counterexample in that altered
   model.
3. **Executable witness.** `witness/` exposes one `Gate.bind` path and the
   adversarial tests check that the supplied witness does not call its effect
   function without `ALLOW`.
4. **TLA+ expression.** `spec/NoDirectBind.tla` expresses the same invariant.
   The checked-in TLC configuration fixes one environment
   (`AuthorityPresent = TRUE`, `EvidenceProved = TRUE`); it is not a receipt for
   all external systems or all possible environments.

## Verify

```bash
python proof/model.py
```

Expected:

```text
[gated]   No-Direct-Bind holds over all 13 reachable states: True
[ungated] direct-bind shortcut produces a violation: True
```

Run the supplied witness tests:

```bash
python -m pip install pytest
python -m pytest adversarial/ -q
```

Optional TLC check, if TLA+ is installed:

```bash
cd spec
tlc NoDirectBind.tla -config NoDirectBind.cfg
```

## Layout

```text
spec/NoDirectBind.tla     model-local TLA+ property
spec/NoDirectBind.cfg     one checked-in TLC configuration
proof/model.py            13-state exhaustive check + altered-model counterexample
witness/                  small executable reference witness
adversarial/              tests against the model and supplied witness
```

## Falsification boundary

A valid challenge to this repository can show that:

- the 13-state enumeration misses a state reachable under its own transition
  rules;
- the invariant fails in the declared model;
- the supplied witness invokes its effect without `ALLOW`; or
- the README describes more than the files establish.

Showing a bypass in an external stack would falsify a claim about that stack,
not this model-local result, unless that stack had first been bound to this
model and enforcement path.

## Claim discipline

- **PROVED:** the invariant holds over all 13 reachable states of the declared
  Python model; the altered model produces a counterexample.
- **TESTED:** the supplied witness passes its adversarial suite when run.
- **PLAUSIBLE:** the pattern may inform the design of a real enforcement path.
- **NOT CLAIMED:** a formal result about real agents, external stacks,
  production non-bypassability, security or deployment.

## License

Apache-2.0.
