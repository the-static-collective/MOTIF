"""REASON-013 source-owned judicial prose snapshots, WITHOUT gold labels.

Snapshots consist of selected, untagged text paragraphs taken from published
US Supreme Court opinions. They are not full opinions. Editorial paragraph
boundaries and a case-level citation are transport metadata, not solutions.
Training: McBoyle (stolen airplane) and 95 Barrels (dried-apple vinegar).
Held out: Nix (tomato tariff), Yates (fish, plurality/concurrence/dissent).

The engine may inspect prose only. Independent evaluator keys are in gold.py
and are NEVER imported by reader.py.
"""
SOURCE_REVISION="motif.reason.adversarial-reader.opinion-prose-v1"

DOCUMENTS={
 "MCBOYLE":{
  "citation":"283 U.S. 25 (1931)",
  "url":"https://www.law.cornell.edu/supremecourt/text/283/25",
  "year":"1931","court":"US_SUPREME_COURT",
  "training":True,
  "paragraphs":[
   "Mr. Justice HOLMES delivered the opinion of the Court.",
   "The petitioner was convicted of transporting an airplane that he knew to have been stolen and was sentenced to serve three years imprisonment and to pay a fine.",
   "A writ of certiorari was granted by this Court on the question whether the National Motor Vehicle Theft Act applies to aircraft.",
   "The question is the meaning of the word vehicle in the phrase any other self-propelled vehicle not designed for running on rails.",
   "But in everyday speech vehicle calls up the picture of a thing moving on land.",
   "It is a vehicle that runs, not something, not commonly called a vehicle, that flies.",
   "Although it is not likely that a criminal will carefully consider the text of the law before he murders or steals, it is reasonable that a fair warning should be given to the world.",
   "Judgment reversed.",
  ],
 },
 "VINEGAR":{
  "citation":"265 U.S. 438 (1924)",
  "url":"https://www.law.cornell.edu/supremecourt/text/265/438",
  "year":"1924","court":"US_SUPREME_COURT",
  "training":True,
  "paragraphs":[
   "Mr. Justice BUTLER delivered the opinion of the Court.",
   "The United States filed information in the District Court for the condemnation of 95 barrels of vinegar.",
   "The information alleged that the vinegar was adulterated. It also alleged that the vinegar was made from dried or evaporated apples, and was misbranded.",
   "The court found that the charge of adulteration was not sustained, but held that the vinegar was misbranded.",
   "The question for decision is whether the vinegar was misbranded.",
   "The statute is plain and direct. Its comprehensive terms condemn every statement, design, and device which may mislead or deceive.",
   "The label was misleading as to the vinegar, its substance and ingredients.",
   "The facts admitted sustain the charge of misbranding.",
   "Judgment reversed.",
  ],
 },
 "NIX":{
  "citation":"149 U.S. 304 (1893)",
  "url":"https://www.law.cornell.edu/supremecourt/text/149/304",
  "year":"1893","court":"US_SUPREME_COURT",
  "training":False,
  "paragraphs":[
   "Mr. Justice GRAY, after stating the facts in the foregoing language, delivered the opinion of the Court.",
   "This was an action brought against the collector of the port of New York to recover back duties paid under protest on tomatoes imported from the West Indies.",
   "The plaintiffs contended tomatoes came within the free list of the tariff act for fruits, green, ripe, or dried.",
   "The single question in this case is whether tomatoes, considered as provisions, are to be classed as vegetables or as fruit, within the meaning of the tariff act of 1883.",
   "The passages cited from the dictionaries define the word fruit as the seed of plants, or that part of plants which contains the seed.",
   "There being no evidence that the words fruit and vegetables have acquired any special meaning in trade or commerce, they must receive their ordinary meaning.",
   "Botanically speaking, tomatoes are the fruit of a vine, just as are cucumbers, squashes, beans, and peas.",
   "But in the common language of the people, whether sellers or consumers of provisions, all these are vegetables.",
   "Judgment affirmed.",
  ],
 },
 "YATES":{
  "citation":"574 U.S. 528 (2015)",
  "url":"https://www.law.cornell.edu/supremecourt/text/13-7451",
  "year":"2015","court":"US_SUPREME_COURT",
  "training":False,
  "paragraphs":[
   "Justice Ginsburg announced the judgment of the Court and delivered an opinion, in which The Chief Justice, Justice Breyer, and Justice Sotomayor join.",
   "John Yates, a commercial fisherman, caught undersized red grouper in federal waters in the Gulf of Mexico.",
   "To prevent federal authorities from confirming that he had harvested undersized fish, Yates ordered a crew member to toss the suspect catch into the sea.",
   "He was charged with, and convicted of, violating 18 U.S.C. §1519.",
   "Yates does not contest his conviction for violating §2232(a), but he maintains that fish are not trapped within the term tangible object, as that term is used in §1519.",
   "A fish is no doubt an object that is tangible; fish can be seen, caught, and handled.",
   "But it would cut §1519 loose from its financial-fraud mooring to hold that it encompasses any and all objects, whatever their size or significance.",
   "A tangible object captured by §1519, we hold, must be one used to record or preserve information.",
   "The judgment of the U.S. Court of Appeals for the Eleventh Circuit is therefore reversed, and the case is remanded for further proceedings.",
   "Justice Alito, concurring in the judgment.",
   "This case can and should be resolved on narrow grounds. Traditional tools of statutory construction confirm that John Yates has the better of the argument.",
   "Applying these canons to §1519's list of nouns, the term tangible object should refer to something similar to records or documents.",
   "A fish does not spring to mind, nor does an antelope, a colonial farmhouse, a hydrofoil, or an oil derrick.",
   "This too points toward filekeeping, not fish.",
   "Justice Kagan, with whom Justice Scalia, Justice Kennedy, and Justice Thomas join, dissenting.",
   "A criminal law, 18 U.S.C. §1519, prohibits tampering with any record, document, or tangible object in an attempt to obstruct a federal investigation.",
   "The term tangible object is broad, but clear. Throughout the U.S. Code and many States' laws, it invariably covers physical objects of all kinds.",
   "A fish is, of course, a discrete thing that possesses physical form.",
   "So the ordinary meaning of the term tangible object in §1519, as no one here disputes, covers fish.",
   "In my view, conventional tools of statutory construction all lead to a more conventional result.",
   "I would apply the statute that Congress enacted and affirm the judgment below.",
  ],
 },
}

def documents(training):
    return {k:v for k,v in DOCUMENTS.items() if v["training"] is training}
