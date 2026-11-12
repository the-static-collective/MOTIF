/* RECIPROCAL-001: local, finite, interpretable research specimen.
   No network, persistent state, pretrained model, or person-level inference. */
(function (root) {
  "use strict";
  // Bit i is the output for (a,b) in row order 00, 01, 10, 11.
  const RULES = Object.freeze({
    ZERO: 0, ONE: 15, A: 12, B: 10, AND: 8, OR: 14,
    XOR: 6, XNOR: 9, NAND: 7, NOR: 1, IMPLIES: 11
  });
  const STARTER = Object.freeze(["A", "B", "AND", "OR", "XOR", "XNOR", "NAND", "NOR"]);
  const INPUTS = Object.freeze(["00", "01", "10", "11"]);
  const PRE = Object.freeze(["ZERO", "A", "AND", "XNOR", "IMPLIES"]);
  const POST = Object.freeze(["ZERO", "A", "B", "AND", "NOR"]);

  function output(mask, row) {
    if (!Number.isInteger(mask) || mask < 0 || mask > 15 ||
        !Number.isInteger(row) || row < 0 || row > 3) throw Error("INVALID_RULE_OR_ROW");
    return (mask >> row) & 1;
  }
  function partition(candidates, row, library) {
    const counts = [0, 0];
    for (const key of candidates) {
      if (!(key in library)) throw Error("UNKNOWN_OPERATOR");
      counts[output(library[key], row)]++;
    }
    const n = counts[0] + counts[1];
    return { row, counts, expectedRemaining: n ? (counts[0] ** 2 + counts[1] ** 2) / n : 0,
             worstRemaining: Math.max(...counts) };
  }
  function rankQuestions(candidates, library = RULES, unused = [0, 1, 2, 3]) {
    return unused.map(row => partition(candidates, row, library))
      .sort((x, y) => x.expectedRemaining - y.expectedRemaining ||
            x.worstRemaining - y.worstRemaining || x.row - y.row);
  }
  function assessHuman(candidates, chosenRow, library = RULES) {
    const rankings = rankQuestions(candidates, library);
    const choice = partition(candidates, chosenRow, library);
    const optimal = rankings[0].expectedRemaining;
    return { correct: Math.abs(choice.expectedRemaining - optimal) < 1e-9,
      chosenRow, expectedRemaining: choice.expectedRemaining, optimal,
      bestRows: rankings.filter(r => Math.abs(r.expectedRemaining - optimal) < 1e-9).map(r => r.row) };
  }
  class Learner {
    constructor(names = STARTER, library = RULES) {
      this.library = Object.assign(Object.create(null), library);
      this.initial = [...names];
      for (const name of this.initial) if (!(name in this.library)) throw Error("UNKNOWN_INITIAL_OPERATOR");
      this.events = [];
      this.pendingConflict = false;
    }
    latest() {
      const observations = new Map();
      for (const event of this.events) if (event.kind === "OBSERVE" || event.kind === "REPLACE")
        observations.set(event.row, event.value);
      return observations;
    }
    candidates() {
      const observed = this.latest();
      return Object.keys(this.library).filter(name =>
        (this.initial.includes(name) || this.events.some(e => e.kind === "ADD_OPERATOR" && e.name === name)) &&
        [...observed].every(([row, value]) => output(this.library[name], row) === value));
    }
    status() {
      if (this.pendingConflict) return "HOLD_CONFLICT";
      const count = this.candidates().length;
      return count === 0 ? "HOLD_OUT_OF_FAMILY" : count === 1 ? "IDENTIFIED" : "UNCERTAIN";
    }
    observe(row, value, source = "local-person", mode = "OBSERVE") {
      if (!Number.isInteger(row) || row < 0 || row > 3 || (value !== 0 && value !== 1))
        throw Error("INVALID_OBSERVATION");
      if (mode !== "OBSERVE" && mode !== "REPLACE") throw Error("BAD_MODE");
      const previous = this.latest().get(row);
      if (previous !== undefined && previous !== value && mode !== "REPLACE") {
        this.events.push({ id: this.events.length + 1, kind: "CONTEST", row, value, source,
                           previous, status: "NOT_ADMITTED" });
        this.pendingConflict = true;
        return this.status();
      }
      if (mode === "REPLACE" && previous === undefined) throw Error("NO_PRIOR_OBSERVATION");
      this.events.push({ id: this.events.length + 1, kind: mode, row, value, source,
                         prior: previous === undefined ? null : previous });
      this.pendingConflict = false;
      return this.status();
    }
    addOperator(name, bits, source = "local-person") {
      if (!/^[A-Z][A-Z0-9_]{0,27}$/.test(name) || name in this.library ||
          !/^[01]{4}$/.test(bits)) throw Error("INVALID_OR_EXISTING_OPERATOR");
      // User-supplied definition, not autonomously invented semantics.
      const mask = bits.split("").reduce((sum, bit, row) => sum | (Number(bit) << row), 0);
      if (Object.values(this.library).includes(mask)) throw Error("DUPLICATE_TRUTH_TABLE");
      this.library[name] = mask;
      this.events.push({ id: this.events.length + 1, kind: "ADD_OPERATOR", name,
                         bits, source, status: "USER_DEFINED_ONLY" });
      return this.status();
    }
    nextQuestion() {
      if (this.status() !== "UNCERTAIN") return null;
      const unseen = [0, 1, 2, 3].filter(row => !this.latest().has(row));
      return unseen.length ? rankQuestions(this.candidates(), this.library, unseen)[0] : null;
    }
    prediction(row) {
      if (this.status() === "HOLD_CONFLICT" || this.status() === "HOLD_OUT_OF_FAMILY") return null;
      const candidates = this.candidates();
      if (candidates.length === 0) return null;
      const answers = [...new Set(candidates.map(k => output(this.library[k], row)))];
      return answers.length === 1 ? answers[0] : null;
    }
    trace() {
      return { status: this.status(), candidates: this.candidates(), question: this.nextQuestion(),
               events: this.events.map(e => ({ ...e })) };
    }
  }
  function runSynthetic(target, policy = "adaptive", initial = STARTER) {
    if (!(target in RULES) || !initial.includes(target)) throw Error("BAD_TARGET");
    const learner = new Learner(initial);
    for (let step = 0; step < 4 && learner.status() === "UNCERTAIN"; step++) {
      const row = policy === "adaptive" ? learner.nextQuestion().row :
        policy === "fixed" ? step : (() => { throw Error("BAD_POLICY"); })();
      learner.observe(row, output(RULES[target], row), "scripted-fixture");
    }
    const untouched = [0, 1, 2, 3].filter(row => !learner.latest().has(row));
    return { target, policy, steps: learner.latest().size, status: learner.status(),
      identified: learner.candidates()[0] === target && learner.status() === "IDENTIFIED",
      actualUntouched: untouched.length,
      untouchedCorrect: untouched.filter(row => learner.prediction(row) === output(RULES[target], row)).length };
  }
  const exported = { RULES, STARTER, INPUTS, PRE, POST, output, partition,
                     rankQuestions, assessHuman, Learner, runSynthetic };
  if (typeof module === "object" && module.exports) module.exports = exported;
  else root.Reciprocal = exported;
})(typeof window === "undefined" ? globalThis : window);
