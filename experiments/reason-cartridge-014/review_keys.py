"""Independent source-owner questions, labels and exact evidence-target substrings.

Only the evaluator imports this module. The reader has no reference to this
file, its correct answer phrases, or the unseen opinion titles. The questions
were composed from publicly reviewed historical texts; this is NOT a blinded,
externally recruited or cryptographically sealed independent benchmark.
Gold means a reviewed relevant source passage, not a legal outcome.
"""
HELDOUT_QUESTIONS=(
 {"id":"K1","case":"KIRBY",
  "question":"How did the Court treat delay of mail caused by a sheriff arresting a murder-indicted carrier?",
  "target":"does not apply to a case of temporary detention",
  "voice":"OPINION_OF_COURT","meaning":"STATUTORY_EXCEPTION_NOT_UNIVERSAL_MAIL_IMMUNITY"},
 {"id":"K2","case":"KIRBY",
  "question":"How did the judges avoid an absurd consequence from literal statutory wording?",
  "target":"reason of the law in such cases should prevail over its letter",
  "voice":"OPINION_OF_COURT","meaning":"CONTEXTUAL_CONSTRUCTION"},
 {"id":"K3","case":"KIRBY",
  "question":"What example about a surgeon drawing blood illustrated limits of a broad prohibition?",
  "target":"surgeon who opened the vein",
  "voice":"OPINION_OF_COURT","meaning":"ILLUSTRATIVE_ANALOGY_NOT_ACTUAL_CASE_HOLDING"},
 {"id":"K4","case":"KIRBY",
  "question":"Did Justice Miller participate in the order or was he absent at the hearing?",
  "target":"Mr. Justice MILLER, having been absent",
  "voice":"OPINION_OF_COURT","meaning":"NONPARTICIPATION_NOTE"},
 {"id":"B1","case":"BALLARD",
  "question":"Could a jury determine whether religious doctrines were true or false under the First Amendment?",
  "target":"So we conclude that the District Court ruled properly",
  "voice":"OPINION_OF_COURT","meaning":"DOCTRINAL_TRUTH_NOT_SUBMITTED_TO_JURY"},
 {"id":"B2","case":"BALLARD",
  "question":"What did the majority say about beliefs people cannot prove by evidence?",
  "target":"Men may believe what they cannot prove",
  "voice":"OPINION_OF_COURT","meaning":"FREE_EXERCISE_PRINCIPLE_NOT_PROOF_OF_MIRACLES"},
 {"id":"B3","case":"BALLARD",
  "question":"What happened to the case on appeal, reversal and remand?",
  "target":"The judgment is reversed and the cause is remanded",
  "voice":"OPINION_OF_COURT","meaning":"REMANDED_NOT_FINAL_ACQUITTAL"},
 {"id":"B4","case":"BALLARD",
  "question":"What did Chief Justice Stone's dissent argue about fraudulent religious fundraising?",
  "target":"I cannot say that freedom of thought and worship includes freedom",
  "voice":"DISSENT","meaning":"STONE_DISSENT_ON_FALSE_RELIGIOUS_REPRESENTATIONS"},
 {"id":"B5","case":"BALLARD",
  "question":"What did Justice Jackson recommend about dismissing the indictment?",
  "target":"I would dismiss the indictment",
  "voice":"DISSENT","meaning":"JACKSON_SEPARATE_DISSENT"},
 {"id":"B6","case":"BALLARD",
  "question":"What disposition did Stone want for the district court guilty verdict?",
  "target":"that of the District Court reinstated",
  "voice":"DISSENT","meaning":"STONE_CONTRARY_DISPOSITION"},
 {"id":"B7","case":"BALLARD",
  "question":"Why did the majority send the matter back with other issues unresolved?",
  "target":"remaining questions were not fully presented",
  "voice":"OPINION_OF_COURT","meaning":"UNRESOLVED_OTHER_APPELLATE_GROUNDS"},
)
NEGATIVE_QUESTIONS=(
 {"id":"HOLD-1","case":"KIRBY",
  "question":"Is the courthouse made of edible cheese under unicorn property law?"},
 {"id":"HOLD-2","case":"BALLARD",
  "question":"Does the courthouse own a dancing sentient blue banana?"},
)
UNANSWERABLE_BUT_RELEVANT=(
 {"id":"B-TRUTH","case":"BALLARD",
  "question":"Did the Court scientifically prove that the alleged supernatural healing actually occurred?"},
)
