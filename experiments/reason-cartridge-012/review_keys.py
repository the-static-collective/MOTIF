"""Evaluator-owned human annotations of short, real judicial opinion excerpts.

NOT imported by model.py. Gold labels are judgments about the tiny excerpt
and its opinion context, not general legal truth or currently binding law.
"""
LABELS={
 "S1":("LEGAL_TREATMENT","ESTOPPEL_REPUTATION","YES"),
 "S2":("PROCEDURAL_POSTURE","MAY_SEEK_RESCISSION","YES"),
 "L1":("PARTY_ALLEGATION","ADVERTISEMENT_CONSTITUTES_OFFER","UNDECIDED"),
 "L2":("PROCEDURAL_POSTURE","LOWER_DECISION_AFFIRMED","YES"),
 "N1":("LEGAL_TREATMENT","COPYRIGHT_STATUTORY_STANDING","NO"),
 "N2":("LEGAL_TREATMENT","ARTICLE_III_STANDING","YES"),
 "P1":("PROCEDURAL_POSTURE","LOWER_DECISION_AFFIRMED","NO"),
 "P2":("SEPARATE_OPINION","DISSENT_DISAGREES","YES"),
 "U1":("LEGAL_TREATMENT","PORNOGRAPHIC_INTENT","NO"),
 "U2":("PROCEDURAL_POSTURE","FORFEITURE_GRANTED","NO"),
 "C1":("LEGAL_TREATMENT","CAFFEINE_ADDED_INGREDIENT","YES"),
 "C2":("UNRESOLVED_FACT_ISSUE","CAFFEINE_HARM_PROVEN","UNDECIDED"),
}
TRAIN_KEYS=("S1","S2","L1","L2","N1","N2","P1","P2")
SEALED_KEYS=("U1","U2","C1","C2")


def labeled_training():
    from corpus import passages
    return tuple((p,LABELS[p["span_id"]][0]) for p in passages(True))


def reference_for(span_id):
    return LABELS[span_id]
