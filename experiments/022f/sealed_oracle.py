"""Sealed evaluator fixtures for MOTIF-022F: not imported by the critic loop.

This simulator returns distinct CALIBRATION and RUN observations; the critic
gets neither the hidden world nor an authority to call this class. Simulated
source names are NOT authenticated real-world identities.
"""
from __future__ import annotations

from dataclasses import dataclass

from feedback import RegisteredTest, ReviewReceipt
from forest import Road
from multiplex import Hypothesis
from chorus import PublicProjection


def modeled_problem():
    """Four invented program states: A(udio) and M(eal) independent binary gates.

    The December 4 real venue permission is already reported granted.
    In this tiny *imaginary* task:
      audio=0 -> acoustic-only; audio=1 -> a provided PA may be used;
      meal=0 -> no food announced; meal=1 -> a meal may be announced.

    These symbols do NOT report actual PA readiness or food permission.
    """
    names = ("00", "01", "10", "11")
    hypotheses = tuple(
        Hypothesis(name, f"A{name[0]}_M{name[1]}", 1.0) for name in names
    )
    audio = Road(
        "AUDIO_PATH_TEST", "ASK", 0.2, {n: n[0] for n in names},
        "synthetic-local-audio-witness",
        prompt="Independent synthetic audio-readiness result?",
    )
    def test(name, cost, source, signal=1, *,
             approved=True, human=False, latency=0):
        predicted = {n: n[signal] if isinstance(signal, int) else signal for n in names}
        return RegisteredTest(
            Road(name, "ASK", cost, predicted, source, allowed=False,
                 prompt="Hypothetical registered inquiry: " + name),
            name.replace("_", " ").capitalize(),
            operator_approved_for_synthetic=approved,
            human_execution_required=human,
            latency_ticks=latency,
        )
    catalog = (
        test("FOOD_SERVICE_GATE", 0.2, "synthetic-food-independent"),
        test("BAD_FOOD_TEST", 0.1, "synthetic-falsifier"),
        test("DRIFT_FOOD_TEST", 0.2, "synthetic-drifting-source"),
        test("HUMAN_FOOD_CONFIRMATION", 0.05, "real-human-hold",
             approved=False, human=True),
        test("SLOW_FOOD_TEST", 0.2, "synthetic-slow-test", latency=1),
        test("REPEAT_AUDIO_TEST", 0.2, audio.origin, signal=0),
        test("NONINFORMATIVE_CHECK", 0.02, "synthetic-busywork", signal="0"),
    )
    return hypotheses, (audio,), catalog


def public_projection() -> PublicProjection:
    return PublicProjection(
        problem="Propose a minimal December 4 Fellowship program without assuming extra permissions.",
        facts=(
            "User reports permission to use the meeting space.",
            "User reports the user and Paula are core organizers.",
            "Smallest safe program can omit food and amplified music.",
        ),
        uncertainties=(
            "Food serving arrangements are not confirmed in the supplied evidence.",
            "PA/access details are not confirmed in the supplied evidence.",
            "Nexus applicant-group eligibility is a separate unresolved decision.",
        ),
        proposed_next="Use small verified steps and never announce optional services as facts.",
    )


class SealedSyntheticOracle:
    """Separate outcome reporter: cannot be constructed from critic text."""
    def __init__(self, hidden_world: str):
        if hidden_world not in ("00", "01", "10", "11"):
            raise ValueError("UNKNOWN_HIDDEN_FIXTURE")
        self._hidden_world = hidden_world
        self.executed: list[tuple[str, str]] = []

    @staticmethod
    def _raw(world: str, test_id: str, phase: str) -> str:
        if world not in ("00", "01", "10", "11"):
            raise ValueError("Unknown synthetic fixture state")
        if phase not in ("CALIBRATION", "RUN"):
            raise ValueError("Unsupported source evidence phase")
        if test_id in ("AUDIO_PATH_TEST", "REPEAT_AUDIO_TEST"):
            return world[0]
        if test_id in ("FOOD_SERVICE_GATE", "BAD_FOOD_TEST",
                       "DRIFT_FOOD_TEST", "SLOW_FOOD_TEST"):
            if test_id == "BAD_FOOD_TEST" and world == "11":
                return "0"
            if test_id == "DRIFT_FOOD_TEST" and phase == "RUN" and world == "11":
                return "0"
            return world[1]
        if test_id == "NONINFORMATIVE_CHECK":
            return "0"
        raise ValueError("Unlicensed synthetic sensor")

    @classmethod
    def calibration(cls, test: RegisteredTest) -> tuple[ReviewReceipt, ...]:
        if test.human_execution_required or not test.operator_approved_for_synthetic:
            return ()
        return tuple(
            ReviewReceipt(
                case_id=f"review-{name}-{rep}",
                world=name, source=test.road.origin,
                outcome=cls._raw(name, test.road.name, "CALIBRATION"),
                cost=test.road.cost,
            )
            for name in ("00", "01", "10", "11") for rep in (0, 1)
        )

    def execute(self, road: Road) -> str:
        # Only registered synthetic source names reach this private evaluator.
        result = self._raw(self._hidden_world, road.name, "RUN")
        self.executed.append((road.name, result))
        return result


class ScriptedCritic:
    """A scripted stand-in for T5, not inference from a real language model."""
    name = "SCRIPTED_CRITIC_NOT_AN_LLM"
    def __init__(self, proposed_id: str = "FOOD_SERVICE_GATE"):
        self.proposed_id = proposed_id

    def generate(self, prompt: str) -> str:
        if prompt.startswith("Return EXACTLY TEST_ID="):
            return "TEST_ID=" + self.proposed_id
        if prompt.startswith("ROLE=OBSERVER."):
            return "Space use was reported granted; food service remains unconfirmed."
        if prompt.startswith("ROLE=HYPEMAN."):
            return "The two core organizers can make a minimal program without optional extras."
        raise ValueError("Unknown scripted test prompt")
