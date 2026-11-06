"""Curated legal-opinion evidence cards for REASON-010.

These are human-reviewed *paraphrase annotations* of real historical opinions,
NOT unstructured machine-read transcripts, current legal advice, or a source
of binding precedent outside the adjudicating forum. The original opinions
are linked for independent human verification. Current law may differ.
"""
from __future__ import annotations

CASES={
 "STAMBOVSKY":{
  "title":"Stambovsky v. Ackley", "citation":"169 A.D.2d 254 (N.Y. App. Div. 1991)",
  "court":"N.Y. App. Div., First Department","year":1991,
  "opinion_url":"https://govt.westlaw.com/nyofficial/Document/I3785d6c8dbd711d9a489ee624f1f6e1a",
  "source_kind":"OFFICIAL_NY_REPORTS","training":True,
  "facts":"A home seller publicly promoted a reputation for hauntings; a buyer sought to undo the sale.",
  "claims":[
   ("S-REP","REPUTATION","COURT_MAJORITY","HOLDING","LEGAL_ESTOPPEL",
    "Seller's publicity about ghosts supported a narrow equitable rescission theory; this was not an empirical experiment proving ghosts."),
   ("S-REPHYPE","REPUTATION","SELLER","PUBLIC_ACCOUNT","REPORTED_EXPERIENCE",
    "The seller described purported paranormal experiences in publications."),
   ("S-RELIEF","DISPOSITION","COURT_MAJORITY","HOLDING","APPELLATE_PROCEDURE",
    "The appellate court reinstated the buyer's rescission cause of action; it did not finally award rescission."),
   ("S-DISSENT","DISPOSITION","DISSENT","SEPARATE_OPINION","APPELLATE_PROCEDURE",
    "The dissent would not reinstate the claim under these facts."),
   ("S-BROKER","BROKER_DUTY","COURT_MAJORITY","HOLDING","LEGAL_DUTY",
    "The real estate broker was not held liable for failing to disclose the reputation."),
  ],
 },
 "LEONARD":{
  "title":"Leonard v. Pepsico", "citation":"210 F.3d 88 (2d Cir. 2000)",
  "court":"U.S. Court of Appeals, Second Circuit","year":2000,
  "opinion_url":"https://law.justia.com/cases/federal/appellate-courts/F3/210/88/483989/",
  "source_kind":"REPRODUCED_APPELLATE_OPINION","training":True,
  "facts":"A soda advertisement showed a Harrier jet for seven million promotional points.",
  "claims":[
   ("L-OFFER","ADVERTISEMENT_OFFER","COURT_MAJORITY","HOLDING","OBJECTIVE_CONTRACT",
    "The advertisement did not constitute an enforceable offer of a fighter jet."),
   ("L-DEMAND","ADVERTISEMENT_OFFER","PLAINTIFF","LITIGANT_POSITION","SUBJECTIVE_DEMAND",
    "The claimant argued that the commercial offered a Harrier jet for Pepsi points."),
   ("L-REASON","ADVERTISEMENT_OFFER","COURT_MAJORITY","REASONING","OBJECTIVE_CONTRACT",
    "The jet depiction was humor that a reasonable observer would not construe as a genuine offer."),
   ("L-DISPOSE","DISPOSITION","COURT_MAJORITY","HOLDING","APPELLATE_PROCEDURE",
    "The Second Circuit affirmed summary judgment for PepsiCo."),
   ("L-PARTY","DISPOSITION","PLAINTIFF","LITIGANT_REQUEST","APPELLATE_PROCEDURE",
    "The plaintiff sought specific performance and delivery of the advertised jet."),
   ("L-WRITING","WRITING_REQUIREMENT","COURT_MAJORITY","HOLDING","CONTRACT_FORMALITY",
    "The alleged arrangement lacked the writing required by New York's Statute of Frauds."),
  ],
 },
 "NARUTO":{
  "title":"Naruto v. Slater", "citation":"888 F.3d 418 (9th Cir. 2018)",
  "court":"U.S. Court of Appeals, Ninth Circuit","year":2018,
  "opinion_url":"https://law.justia.com/cases/federal/appellate-courts/ca9/16-15469/16-15469-2018-04-23.html",
  "source_kind":"REPRODUCED_APPELLATE_OPINION","training":False,
  "facts":"A macaque allegedly took selfies on a photographer's camera; suit alleged copyright infringement.",
  "claims":[
   ("N-ARTICLE","ARTICLE_III","COURT_MAJORITY","HOLDING","CONSTITUTIONAL_STANDING",
    "Under binding circuit precedent, the panel treated the pleaded allegations as sufficient for Article III standing."),
   ("N-STATUTE","COPYRIGHT_STATUTE","COURT_MAJORITY","HOLDING","STATUTORY_STANDING",
    "The Copyright Act did not authorize nonhuman animals to bring this infringement claim."),
   ("N-CONCUR","ARTICLE_III","CONCURRENCE","SEPARATE_OPINION","NEXT_FRIEND_JURISDICTION",
    "A concurring judge would dismiss for lack of jurisdiction based on next-friend standing concerns."),
   ("N-CLAIM","COPYRIGHT_STATUTE","PLAINTIFF","LITIGANT_POSITION","STATUTORY_STANDING",
    "The action asserted copyright interests on behalf of the macaque."),
   ("N-DISPOSE","DISPOSITION","COURT_MAJORITY","HOLDING","APPELLATE_PROCEDURE",
    "The appellate court affirmed dismissal of the copyright infringement claim."),
  ],
 },
 "PIERSON":{
  "title":"Pierson v. Post", "citation":"3 Cai. R. 175 (N.Y. 1805)",
  "court":"N.Y. Supreme Court of Judicature","year":1805,
  "opinion_url":"https://law.justia.com/cases/new-york/other-courts/1805/3-caines-175.html",
  "supplement_url":"https://history.nycourts.gov/case/pierson-v-post/",
  "source_kind":"HISTORICAL_OPINION_AND_COURT_SOCIETY_SUMMARY","training":False,
  "facts":"One hunter pursued a fox; another captured and killed it, prompting a property dispute.",
  "claims":[
   ("P-PURSUIT","WILD_ANIMAL_POSSESSION","COURT_MAJORITY","HOLDING","PROPERTY_OCCUPANCY",
    "Mere pursuit of a wild fox did not establish the enforceable property right claimed by Post."),
   ("P-DISSENT","WILD_ANIMAL_POSSESSION","DISSENT","SEPARATE_OPINION","PROPERTY_OCCUPANCY",
    "The dissent favored recognizing rights arising from hot pursuit in these circumstances."),
   ("P-ARGUMENT","WILD_ANIMAL_POSSESSION","PLAINTIFF","LITIGANT_POSITION","PROPERTY_OCCUPANCY",
    "Post argued that his ongoing chase gave him the superior right to the fox."),
   ("P-DISPOSE","DISPOSITION","COURT_MAJORITY","HOLDING","APPELLATE_PROCEDURE",
    "The higher court reversed the earlier ruling in Post's favor."),
  ],
 },
}

QUERY_SPECS={
 "STAMBOVSKY":(("REPUTATION","COURT_MAJORITY","HOLDING","LEGAL_ESTOPPEL","S-REP"),
               ("DISPOSITION","COURT_MAJORITY","HOLDING","APPELLATE_PROCEDURE","S-RELIEF"),
               ("BROKER_DUTY","COURT_MAJORITY","HOLDING","LEGAL_DUTY","S-BROKER")),
 "LEONARD":(("ADVERTISEMENT_OFFER","COURT_MAJORITY","HOLDING","OBJECTIVE_CONTRACT","L-OFFER"),
            ("DISPOSITION","COURT_MAJORITY","HOLDING","APPELLATE_PROCEDURE","L-DISPOSE"),
            ("WRITING_REQUIREMENT","COURT_MAJORITY","HOLDING","CONTRACT_FORMALITY","L-WRITING")),
 "NARUTO":(("ARTICLE_III","COURT_MAJORITY","HOLDING","CONSTITUTIONAL_STANDING","N-ARTICLE"),
           ("COPYRIGHT_STATUTE","COURT_MAJORITY","HOLDING","STATUTORY_STANDING","N-STATUTE"),
           ("DISPOSITION","COURT_MAJORITY","HOLDING","APPELLATE_PROCEDURE","N-DISPOSE")),
 "PIERSON":(("WILD_ANIMAL_POSSESSION","COURT_MAJORITY","HOLDING","PROPERTY_OCCUPANCY","P-PURSUIT"),
            ("WILD_ANIMAL_POSSESSION","DISSENT","SEPARATE_OPINION","PROPERTY_OCCUPANCY","P-DISSENT"),
            ("DISPOSITION","COURT_MAJORITY","HOLDING","APPELLATE_PROCEDURE","P-DISPOSE")),
}

OPINION_CARD_REVISION="motif.reason.strange-law-curated-opinions.v1"
