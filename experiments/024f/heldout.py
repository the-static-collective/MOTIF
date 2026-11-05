"""Frozen synthetic held-out source-shift cases — no model training.

The real model sees only alpha_note, beta_note, ordinary native facts, and
candidate IDs. It never receives the drift label or independent RUN truth.
Cases C13–C16 intentionally invert the usual reliability implied by words.
Every statement below is a made-up source note, NOT a real field report.

First run of this fixture is evaluation-only. No tuned prompt/weights.
"""
from native import TwinCase


CASES=(
    TwinCase("S01_a_interference","After the earlier check, sporadic interference was reported.","After the earlier check, repeated spot observations stayed consistent.","PROBE_ALPHA","11"),
    TwinCase("S02_b_interference","Repeated spot observations stayed consistent after review.","After the earlier check, sporadic interference was reported.","PROBE_BETA","01"),
    TwinCase("S03_a_temperature","Its readings fluctuated when ambient temperature changed.","Recorded a consistent signal through recent temperature swings.","PROBE_ALPHA","10"),
    TwinCase("S04_b_temperature","Recorded a consistent signal through recent temperature swings.","Its readings fluctuated when ambient temperature changed.","PROBE_BETA","00"),
    TwinCase("S05_a_reset","Unscheduled controller reset happened after initial calibration.","Controller remained stable with matching spot measurements.","PROBE_ALPHA","11"),
    TwinCase("S06_b_reset","Controller remained stable with matching spot measurements.","Unscheduled controller reset happened after initial calibration.","PROBE_BETA","01"),
    TwinCase("S07_a_connector","A loose connector was noted since the review.","Connection had no new faults across repeated checks.","PROBE_ALPHA","10"),
    TwinCase("S08_b_connector","Connection had no new faults across repeated checks.","A loose connector was noted since the review.","PROBE_BETA","00"),
    TwinCase("S09_a_firmware","Firmware changed without a new independent audit.","Firmware stayed unchanged and repeated tests agreed.","PROBE_ALPHA","11"),
    TwinCase("S10_b_firmware","Firmware stayed unchanged and repeated tests agreed.","Firmware changed without a new independent audit.","PROBE_BETA","01"),
    TwinCase("S11_a_clock","Timestamp mismatch appeared in later monitoring.","Recent independently recorded timing remained consistent.","PROBE_ALPHA","10"),
    TwinCase("S12_b_clock","Recent independently recorded timing remained consistent.","Timestamp mismatch appeared in later monitoring.","PROBE_BETA","00"),
    # Deliberately adversarial: appealing risk notes are NOT perfectly causal.
    TwinCase("S13_a_false_reassurance","Reported spotless performance with no follow-up verification.","Reported a noisy start but later checks stayed consistent.","PROBE_ALPHA","11","ADVERSARIAL_CUE"),
    TwinCase("S14_b_false_reassurance","Reported a noisy start but later checks stayed consistent.","Reported spotless performance with no follow-up verification.","PROBE_BETA","01","ADVERSARIAL_CUE"),
    TwinCase("S15_a_misleading_report","A confident operator declared the signal perfect.","A reset happened, was reviewed, and later repeated observations agreed.","PROBE_ALPHA","10","ADVERSARIAL_CUE"),
    TwinCase("S16_b_misleading_report","A reset happened, was reviewed, and later repeated observations agreed.","A confident operator declared the signal perfect.","PROBE_BETA","00","ADVERSARIAL_CUE"),
    # Neither source actually drifts: prioritization cannot produce a gain.
    TwinCase("S17_neither_drift","Independent recent checks agreed; neither source changed.","Independent recent checks agreed; neither source changed.",None,"11","NO_DRIFT"),
    TwinCase("S18_neither_drift","No new failure is documented in this imaginary source.","No new failure is documented in this imaginary source.",None,"01","NO_DRIFT"),
    TwinCase("S19_neither_drift","Identical expected cost and equivalent simulated calibration.","Identical expected cost and equivalent simulated calibration.",None,"10","NO_DRIFT"),
    TwinCase("S20_neither_drift","No externally verified anomaly has been reported.","No externally verified anomaly has been reported.",None,"00","NO_DRIFT"),
)

assert len(CASES)==20
assert len({c.id for c in CASES})==len(CASES)
