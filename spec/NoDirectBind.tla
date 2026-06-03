-------------------------- MODULE NoDirectBind --------------------------
(***************************************************************************)
(* Formal specification of the No-Direct-Bind theorem.                     *)
(*                                                                         *)
(* THEOREM 1 (No-Direct-Bind):                                             *)
(*   An unresolved latent intent cannot bind to a terminal action.         *)
(*   The system enters "executed" only via a transition guarded by         *)
(*   resolvedAllow = TRUE.                                                  *)
(*                                                                         *)
(* The safety invariant NoDirectBind is checked by TLC over every          *)
(* reachable state. The "ungated" action Direct (commented in) is the      *)
(* deliberate falsifier: enabling it makes TLC report a counterexample.    *)
(***************************************************************************)
EXTENDS Naturals

CONSTANTS AuthorityPresent, EvidenceProved   \* booleans: the environment

VARIABLES phase, resolvedAllow

Phases == {"IDLE", "INTENT", "RESOLVED", "EXECUTED"}

TypeOK ==
    /\ phase \in Phases
    /\ resolvedAllow \in BOOLEAN

Init ==
    /\ phase = "IDLE"
    /\ resolvedAllow = FALSE

Form ==                                  \* an intent forms
    /\ phase = "IDLE"
    /\ phase' = "INTENT"
    /\ UNCHANGED resolvedAllow

Resolve ==                               \* the gate evaluates authority+evidence
    /\ phase = "INTENT"
    /\ phase' = "RESOLVED"
    /\ resolvedAllow' = (AuthorityPresent /\ EvidenceProved)

Commit ==                                \* the ONLY guarded edge into EXECUTED
    /\ phase = "RESOLVED"
    /\ resolvedAllow = TRUE
    /\ phase' = "EXECUTED"
    /\ UNCHANGED resolvedAllow

Halt ==                                  \* fail-closed: not allowed -> stay put
    /\ phase = "RESOLVED"
    /\ resolvedAllow = FALSE
    /\ UNCHANGED <<phase, resolvedAllow>>

Next == Form \/ Resolve \/ Commit \/ Halt

(***************************************************************************)
(* THE FALSIFIER. Uncomment Direct and add it to Next to confirm TLC       *)
(* reports a violation — proving the invariant is meaningful and the gate  *)
(* is load-bearing.                                                        *)
(*                                                                         *)
(* Direct ==                                                               *)
(*     /\ phase = "INTENT"                                                  *)
(*     /\ phase' = "EXECUTED"                                              *)
(*     /\ UNCHANGED resolvedAllow                                          *)
(***************************************************************************)

Spec == Init /\ [][Next]_<<phase, resolvedAllow>>

(***************************************************************************)
(* SAFETY INVARIANT — the No-Direct-Bind property.                         *)
(*   If we have executed, authority must have resolved to ALLOW.           *)
(***************************************************************************)
NoDirectBind == (phase = "EXECUTED") => (resolvedAllow = TRUE)

=============================================================================
