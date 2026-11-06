"""Independent historical-text review keys, never imported by the reader.

These annotations reflect a researcher's assessment of selected source
paragraphs. They are not extracted or supplied to the inference component.
"""
NEW_EVALUATION={
 "NIX":{
   "speakers":{"GRAY":{"role":"OPINION_OF_COURT","explicit_votes":1,
                       "interpretive_signals":[],
                       "disposition_signals":["AFFIRMANCE"]}},
   "source_layers":["BOTANICAL_FRUIT","ORDINARY_VEGETABLE"],
   "legal_question":"Whether the 1883 tariff treated tomatoes as vegetables",
   "botanical_vs_tariff_not_one_polarity":True,
 },
 "YATES":{
   "speakers":{
      "GINSBURG":{"role":"JUDGMENT_ANNOUNCER","explicit_votes":4,
                  "interpretive_signals":["RESTRICTED_SCOPE"],
                  "disposition_signals":["REVERSAL"]},
      "ALITO":{"role":"CONCURRENCE_IN_JUDGMENT","explicit_votes":1,
               "interpretive_signals":["RESTRICTED_SCOPE"],
               "disposition_signals":[]},
      "KAGAN":{"role":"DISSENT","explicit_votes":4,
               "interpretive_signals":["EXPANSIVE_SCOPE"],
               "disposition_signals":["AFFIRMANCE"]},
   },
   "judgment_alignment":[5,4],
   "doctrinal_majority_cannot_be_assumed_from_plurality":True,
   "competing_voiced_reasons":True,
 }
}

TRAINING_CONTROLS={
 "MCBOYLE":{"judges":["HOLMES"],"disposition":"REVERSAL"},
 "VINEGAR":{"judges":["BUTLER"],"disposition":"REVERSAL"},
}
