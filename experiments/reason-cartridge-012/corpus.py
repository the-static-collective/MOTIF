"""REASON-012: real judicial-opinion quotation snippets, with URL/paragraph anchors.

These are SHORT verbatim substrings verified against published judicial opinion
text. The corpus is not a full-opinion reader, a current-law database or a
court-authenticated feed. Independent labels live in review_keys.py and are
NOT imported by the learning module.

Training: Stambovsky, Leonard, Naruto, Pierson (known from REASON-010).
New cases held out: Ulysses book seizure and forty barrels of Coca-Cola.
All references are historical; no output is legal advice.
"""
SOURCE_REVISION="motif.reason.actual-opinions.quoted-snippets.v1"

OPINIONS={
 "STAMBOVSKY":{
  "name":"Stambovsky v. Ackley","citation":"169 A.D.2d 254 (N.Y. App. Div. 1991)",
  "court":"NY_APP_DIV","year":1991,"train":True,
  "url":"https://law.justia.com/cases/new-york/appellate-division-first-department/1991/169-a-d-2d-254-572-n-y-s-2d-672.html",
  "spans":[
   ("S1","defendant is estopped to deny their existence and, as a matter of law, the house is haunted","majority opinion, paragraph beginning Whether the source"),
   ("S2","allow the buyer to seek rescission of the contract of sale","majority opinion, paragraph beginning While I agree"),
  ],
 },
 "LEONARD":{
  "name":"Leonard v. Pepsico","citation":"210 F.3d 88 (2d Cir. 2000)",
  "court":"US_CA2","year":2000,"train":True,
  "url":"https://tortwell.com/cases/210-f3d-88",
  "spans":[
   ("L1","Plaintiff-appellant John D.R. Leonard alleges that the ad was an offer","opinion, numbered paragraph 6"),
   ("L2","We affirm for substantially the reasons stated in Judge Wood's opinion","opinion, numbered paragraph 8"),
  ],
 },
 "NARUTO":{
  "name":"Naruto v. Slater","citation":"888 F.3d 418 (9th Cir. 2018)",
  "court":"US_CA9","year":2018,"train":True,
  "url":"https://law.justia.com/cases/federal/appellate-courts/ca9/16-15469/16-15469-2018-04-23.html",
  "spans":[
   ("N1","lacks statutory standing under the Copyright Act","opinion by Judge Bea, opening paragraph"),
   ("N2","the monkey's claim has standing under Article III of the United States Constitution","opinion by Judge Bea, opening paragraph"),
  ],
 },
 "PIERSON":{
  "name":"Pierson v. Post","citation":"3 Cai. R. 175 (N.Y. 1805)",
  "court":"NY_SUPREME_1805","year":1805,"train":True,
  "url":"https://law.justia.com/cases/new-york/other-courts/1805/3-caines-175.html",
  "spans":[
   ("P1","We are of opinion the judgment below was erroneous, and ought to be reversed","opinion by Tompkins J."),
   ("P2","My opinion differs from that of the court","opinion by Livingston J., dissent"),
  ],
 },
 "ULYSSES":{
  "name":"United States v. One Book Called Ulysses",
  "citation":"5 F. Supp. 182 (S.D.N.Y. 1933)",
  "court":"US_SDNY","year":1933,"train":False,
  "url":"https://law.justia.com/cases/federal/district-courts/FSupp/5/182/2250768/",
  "spans":[
   ("U1","I hold, therefore, that it is not pornographic","Woolsey J., section III"),
   ("U2","the government's motion for a decree of forfeiture and destruction is denied","Woolsey J., opening decree"),
  ],
 },
 "COCA":{
  "name":"United States v. Forty Barrels and Twenty Kegs of Coca-Cola",
  "citation":"241 U.S. 265 (1916)",
  "court":"US_SUPREME","year":1916,"train":False,
  "url":"https://www.law.cornell.edu/supremecourt/text/241/265",
  "spans":[
   ("C1","We see no escape from the conclusion that it is an 'added' ingredient","Hughes J., analysis of adulteration"),
   ("C2","the question was plainly one of fact","Hughes J., caffeine harm issue reserved for jury"),
  ],
 },
}


def passages(train):
    result=[]
    for case_id,opinion in OPINIONS.items():
        if opinion["train"] is not train:
            continue
        for span_id,quote,locator in opinion["spans"]:
            result.append({
                "span_id":span_id,
                "case_id":case_id,
                "text":quote,
                "court":opinion["court"],
                "year":opinion["year"],
                "citation":opinion["citation"],
                "opinion_url":opinion["url"],
                "paragraph_locator":locator,
                "quote_kind":"SHORT_VERBATIM_JUDICIAL_OPINION_FRAGMENT",
                "word_count":len(quote.split()),
                "source_revision":SOURCE_REVISION,
                "remote_exact_match_checked_during_curation":True,
                "current_law_not_verified":True,
            })
    return tuple(result)
