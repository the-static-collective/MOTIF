"""VOID-005 — successful defenses provoke enemy counter-moves.

Author-built bounded sandbox, no neural learning, real-world action, or
unverified claim promotion. Native MOTIF-003 scores hypothetical affordances.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from hashlib import sha256
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "void004"))
from waves import (FortOwner, GATES, WAVES, MAX_ATTEMPTS, TARGET_ATTEMPTS,
                   RELAY_COVERAGE, HUB, public_route, seal, verified, native003)

DEV_SEEDS = (51001, 51019, 51031, 51047)
TEST_SEEDS = tuple(93001 + 29 * i for i in range(16))
REGIMES = ("stable", "reactive", "reactive_deceptive")
POLICIES = ("motif_native", "classical_voi", "classical_stale")
FIRST_SHIFT, SECOND_SHIFT = 14, 55


def pick(seed, tag, size):
    return int(sha256(f"void005-private:{seed}:{tag}".encode()).hexdigest(), 16) % size


class DynamicOwner(FortOwner):
    """Truth belongs to the simulator; a relay's report can be false."""
    def __init__(self, seed, regime):
        if seed not in DEV_SEEDS + TEST_SEEDS or regime not in REGIMES:
            raise ValueError("UNDECLARED_WORLD")
        # Ancestor owner only permits VOID-004's old/tested seeds.
        self._lanes = {w:GATES[pick(seed, f"initial-{w}", 4)] for w in range(1, WAVES+1)}
        self.seed, self.regime = seed, regime
        self.attempt, self.sequence, self.source_epoch = 0, 0, 0
        self.phase, self.position, self.turn = "not_started", HUB, 0
        self.current_wave, self.sonar_left, self.relay_used = 1, 0, False
        self.successful_defenses = 0
        self.triggered = set()
        self.changed_waves = []  # For evaluation only, never given to policies
        self.false_relay_claims = 0

    def public_view(self):
        from waves import MAP
        return {"map":MAP, "waves":WAVES, "max_attempts":MAX_ATTEMPTS,
                "regime_family":"POSSIBLY_ADAPTIVE_FALLIBLE_SOURCES",
                "known_rules":{"shifts_only_between_attempts":True,
                               "at_most_two_single_wave_rotations":True,
                               "relay_reports_may_be_wrong":True},
                "attempt":self.attempt, "source_epoch":self.source_epoch}

    def _receipt(self, kind, **kwargs):
        self.sequence += 1
        row = {"source":"AUTHOR_BUILT_FORTRESS_ENGINE", "kind":kind,
               "attempt":self.attempt, "sequence":self.sequence,
               "source_epoch":self.source_epoch, **kwargs}
        row["seal"] = seal(row)
        return row

    def _rotate(self, tag, candidates):
        wave = candidates[pick(self.seed, tag, len(candidates))]
        before = self._lanes[wave]
        self._lanes[wave] = GATES[(GATES.index(before) + 1 +
                                   pick(self.seed, tag + "rotation", 3)) % 4]
        self.source_epoch += 1
        self.changed_waves.append({"after_attempt":self.attempt, "wave":wave,
                                   "previous":before, "current":self._lanes[wave],
                                   "source_epoch":self.source_epoch})
        self.triggered.add(tag)

    def begin(self):
        if self.regime != "stable" and self.phase in ("failed", "cleared"):
            # The *successes* on this particular policy's past attempts,
            # not merely the preselected attempt number, provoke a counter-move.
            if self.successful_defenses >= FIRST_SHIFT and "first" not in self.triggered:
                self._rotate("first", (2, 4, 7, 9, 11))
            if self.successful_defenses >= SECOND_SHIFT and "second" not in self.triggered:
                self._rotate("second", (5, 8, 13, 17, 22))
        return super().begin()

    def read_relay(self):
        report = super().read_relay()
        if self.regime == "reactive_deceptive" and self.attempt <= 5:
            rid = report["relay"]
            selected = RELAY_COVERAGE[rid][pick(self.seed, "liar-" + rid, 3)]
            claims = []
            for wave, gate in report["facts"]:
                if wave == selected:
                    gate = GATES[(GATES.index(gate) + 1) % 4]
                    self.false_relay_claims += 1
                claims.append([wave, gate])
            report["facts"] = claims
            # Re-sealed by the source that is lying: hash-consistent falsehood.
            report["seal"] = seal({k:v for k,v in report.items() if k != "seal"})
        return report

    def defend(self, gate):
        result = super().defend(gate)
        self.successful_defenses += int(result["held"])
        return result


@dataclass
class EpistemicLedger:
    """Append-only verified source *receipts*, not infallible source claims."""
    latest: dict = field(default_factory=dict)
    history: list = field(default_factory=list)
    visited_relays: set = field(default_factory=set)
    epoch: int = 0
    conflicts: int = 0
    epochs_detected: int = 0
    source_downgrade: int = 0

    def learn(self, receipt):
        if not verified(receipt) or receipt.get("source") != "AUTHOR_BUILT_FORTRESS_ENGINE":
            raise ValueError("UNVERIFIED_RECEIPT")
        epoch = receipt["source_epoch"]
        if epoch < self.epoch:
            raise ValueError("REPLAYED_PAST_EPOCH_RECEIPT")
        if epoch > self.epoch:
            self.epochs_detected += 1
            self.epoch = epoch
        kind = receipt["kind"]
        if kind == "RELAY":
            rid = receipt["relay"]
            if (rid not in RELAY_COVERAGE or
                tuple(w for w,_ in receipt["facts"]) != RELAY_COVERAGE[rid]):
                raise ValueError("WRONG_RELAY_SCOPE")
            self.visited_relays.add(rid)
            observations = [(w, g, "fallible_relay") for w,g in receipt["facts"]]
        elif kind in ("SONAR", "DEFEND"):
            observations = [(receipt["wave"],
                             receipt["gate"] if kind=="SONAR" else receipt["actual_gate"],
                             "owner_verified")]
        else:
            observations = []
        for wave, gate, tier in observations:
            if not 1 <= wave <= WAVES or gate not in GATES:
                raise ValueError("INVALID_WAVE_CLAIM")
            earlier = self.latest.get(wave)
            if earlier and earlier["gate"] != gate:
                self.conflicts += 1
                if earlier["tier"] == "fallible_relay" and tier == "owner_verified":
                    self.source_downgrade += 1
            if (not earlier or epoch > earlier["epoch"] or
                tier == "owner_verified" or earlier["tier"] != "owner_verified"):
                self.latest[wave] = {"gate":gate, "tier":tier, "epoch":epoch,
                                     "attempt":receipt["attempt"], "sequence":receipt["sequence"]}
        self.history.append(receipt)

    def predict(self, wave):
        row = self.latest.get(wave)
        return row["gate"] if row else None

    def confidence(self, wave, stale_ablated=False):
        row = self.latest.get(wave)
        if not row:
            return .25
        if stale_ablated:
            return 1.0
        if row["epoch"] < self.epoch:
            return .74 if row["tier"] == "owner_verified" else .56
        if row["tier"] == "owner_verified":
            return 1.0
        return .70 if self.source_downgrade else .86


def projected_score(ledger, relay, attempts_left, stale=False):
    """Conventional expected consecutive defenses plus 2-horizon info dividend."""
    probabilities = [ledger.confidence(w, stale) for w in range(1,WAVES+1)]
    proposed = probabilities[:]
    if relay is not None:
        for w in RELAY_COVERAGE[relay]:
            proposed[w-1] = max(proposed[w-1], .70 if ledger.source_downgrade else .86)
    def progress(probs, sonar):
        alive=1.0
        total=0.0
        for p in probs:
            if sonar and p < .99:
                sonar=False
                p=1.0
            alive *= p
            total += alive
        return total
    immediate = progress(proposed, relay is None)
    future = progress(proposed, True) - progress(probabilities, True)
    return immediate + .70 * min(max(0,attempts_left-1), 3) * future


def relay_choice(ledger, policy, attempts_left):
    available=(None,) + tuple(r for r in sorted(RELAY_COVERAGE)
                              if r not in ledger.visited_relays)
    if policy in ("classical_stale","classical_voi"):
        stale = policy == "classical_stale"
        return max(available, key=lambda r:(projected_score(ledger,r,attempts_left,stale),
                                            0 if r is None else 1))
    if policy != "motif_native":
        raise ValueError("UNDECLARED_POLICY")
    relays = [r for r in available if r]
    if not relays:
        return None
    native = native003()  # original repository implementation
    initial = frozenset({("witnessed",str(w)) for w,item in ledger.latest.items()
                         if item["tier"]=="owner_verified" and item["epoch"]==ledger.epoch})
    def possibilities(state, _verbs):
        for rid in relays:
            if ("visited",rid) in state:
                continue
            successor=set(state)
            successor.add(("visited",rid))
            for w in RELAY_COVERAGE[rid]:
                successor.add(("potential_intel",str(w)))
                successor.add(("skill",f"recheck_{w}"))
            yield (f"inspect:{rid}", (), frozenset(successor))
    def utility(state, _initial):
        potential={int(z) for tag,z in state if tag=="potential_intel"}
        confirmed={int(z) for tag,z in state if tag=="witnessed"}
        return sum((WAVES+1-w)/WAVES for w in potential-confirmed)
    rows=native.analyze_first_moves(initial,tuple(relays),possibilities,utility,
                                   horizon=min(2,max(1,attempts_left)),max_worlds=64)
    by_relay={row["operator"].split(":",1)[1]:row for row in rows
              if row["operator"].startswith("inspect:")}
    if not by_relay: return None
    def combined(rid):
        row=by_relay[rid]
        return (projected_score(ledger,rid,attempts_left)
                + .025*len(row["new_affordances"])
                + .010*len(row["new_skill_facts"]))
    candidate=max(by_relay,key=lambda rid:(combined(rid),-ord(rid)))
    return candidate if combined(candidate) >= projected_score(ledger,None,attempts_left) else None


def run_case(seed, regime, policy, receipts=True):
    if seed not in DEV_SEEDS + TEST_SEEDS or regime not in REGIMES or policy not in POLICIES:
        raise ValueError("UNDECLARED_TRIAL")
    owner=DynamicOwner(seed,regime)
    memory=EpistemicLedger()
    trials=[]
    for n in range(1,MAX_ATTEMPTS+1):
        evidence=[]
        def note(row):
            memory.learn(row)
            if receipts: evidence.append(row)
            return row
        note(owner.begin())
        relay=relay_choice(memory,policy,MAX_ATTEMPTS+1-n)
        if relay:
            for move in public_route(relay):
                note(owner.walk(move))
            note(owner.read_relay())
        note(owner.start_waves())
        breached=None; held=0; sonar_uses=0; uncertain=0
        for w in range(1,WAVES+1):
            conf=memory.confidence(w,stale_ablated=(policy=="classical_stale"))
            if conf < .90: uncertain+=1
            if owner.sonar_left and conf < .90:
                note(owner.sonar());sonar_uses+=1
            gate=memory.predict(w) or "N"
            result=note(owner.defend(gate))
            if result["held"]: held+=1
            else:
                breached=w
                break
        trials.append({"attempt":n,"relay":relay,"waves_held":held,
                       "breached_at":breached,"rechecked_with_sonar":sonar_uses,
                       "unknown_or_uncertain_encounters":uncertain,
                       "epoch":memory.epoch,"conflicts_to_date":memory.conflicts,
                       "verified_receipts":evidence})
        if breached is None:
            break
    completed=next((x["attempt"] for x in trials if x["breached_at"] is None),None)
    return {"seed":seed,"regime":regime,"policy":policy,
            "cleared_at":completed,"by_ten":completed is not None and completed<=TARGET_ATTEMPTS,
            "by_fourteen":completed is not None,
            "restricted_attempts":completed or MAX_ATTEMPTS+1,
            "attempts":trials,"observed_epochs":memory.epochs_detected,
            "evidence_conflicts":memory.conflicts,"source_downgrades":memory.source_downgrade,
            "source_claims_false_evaluator_only":owner.false_relay_claims,
            "adversary_changes_evaluator_only":owner.changed_waves,
            "cumulative_held":owner.successful_defenses,
            "model_calls":0,"real_world_actions":0,
            "source":"AUTHOR_AUTHORED_REACTIVE_FORTRESS_NOT_EXTERNAL_GAME"}


def benchmark(split="development", detailed=False):
    if split not in ("development","heldout"):
        raise ValueError("INVALID_SPLIT")
    seeds=DEV_SEEDS if split=="development" else TEST_SEEDS
    rows=[run_case(seed,regime,policy,receipts=detailed)
          for seed in seeds for regime in REGIMES for policy in POLICIES]
    groups={}
    for regime in REGIMES:
        groups[regime]={}
        for policy in POLICIES:
            subset=[r for r in rows if r["regime"]==regime and r["policy"]==policy]
            groups[regime][policy]={
                "n":len(subset),
                "clear_by_10":sum(r["by_ten"] for r in subset),
                "clear_by_14":sum(r["by_fourteen"] for r in subset),
                "mean_restricted_attempts":round(sum(r["restricted_attempts"] for r in subset)/len(subset),6),
                "observed_epoch_changes":sum(r["observed_epochs"] for r in subset),
                "observed_conflicts":sum(r["evidence_conflicts"] for r in subset)}
    result={"experiment":"VOID-005","split":split,"regimes":REGIMES,
            "policies":POLICIES,"worlds_per_regime":len(seeds),
            "cases":len(rows),"summary":groups,
            "truth_changes_depend_on_prior_defenses":True,
            "some_relay_reports_deliberately_lie":True,
            "actual_native_motif003":True,"llm_calls":0,"real_world_actions":0,
            "independently_authored_env":False,
            "scoped_limits":"Researcher-authored deterministic reactive world; receipt hash is not source truth; classical policies are not globally optimal; no external acts.",
            "rows":rows}
    result["seal"]=seal(result)
    return result


if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--split",choices=("development","heldout"),default="development")
    parser.add_argument("--full-receipts",action="store_true")
    args=parser.parse_args()
    print(json.dumps(benchmark(args.split,args.full_receipts),sort_keys=True,indent=2))
