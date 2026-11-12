"use strict";
const assert = require("node:assert/strict");
const R = require("./reciprocal.js");

const tests = [];
function test(title, fn) { tests.push([title, fn]); }
test("8 actual scripted pupils identify only via sequential observations", () => {
  for (const name of R.STARTER) {
    for (const policy of ["adaptive", "fixed"]) {
      const result = R.runSynthetic(name, policy);
      assert.equal(result.identified, true, JSON.stringify(result));
      assert.equal(result.untouchedCorrect, result.actualUntouched);
      assert.ok(result.steps >= 1 && result.steps <= 4);
    }
  }
});
test("adaptive genuine decision selection saves questions vs a fixed classical baseline", () => {
  const adaptive = R.STARTER.reduce((s, name) => s + R.runSynthetic(name, "adaptive").steps, 0);
  const fixed = R.STARTER.reduce((s, name) => s + R.runSynthetic(name, "fixed").steps, 0);
  assert.equal(adaptive, 24);
  assert.equal(fixed, 27);
  // A matched classical information-gain planner implements the SAME calculation:
  // no claim of a novel or superior optimization algorithm.
});
test("human pre/post questions have genuinely different unique optima", () => {
  assert.deepEqual(R.assessHuman(R.PRE, 0).bestRows, [0]);
  assert.deepEqual(R.assessHuman(R.POST, 3).bestRows, [3]);
  assert.equal(R.assessHuman(R.PRE, 1).correct, false);
  assert.equal(R.assessHuman(R.POST, 0).correct, false);
});
test("a wrong prediction does not erase the person's observed evidence", () => {
  const learner = new R.Learner();
  assert.equal(learner.observe(1, 1), "UNCERTAIN");
  const snapshot = JSON.stringify(learner.trace());
  assert.equal(learner.observe(1, 0), "HOLD_CONFLICT");
  assert.equal(learner.latest().get(1), 1);
  assert.equal(learner.prediction(1), null);
  assert.equal(learner.nextQuestion(), null);
  assert.ok(learner.trace().events.at(-1).status === "NOT_ADMITTED");
  assert.notEqual(snapshot, JSON.stringify(learner.trace()));
  assert.equal(learner.observe(1, 0, "person-explicit-correction", "REPLACE"), "UNCERTAIN");
  assert.equal(learner.latest().get(1), 0);
  assert.equal(learner.trace().events.at(-1).prior, 1);
});
test("contradiction outside initial grammar produces HOLD, not fabricated consensus", () => {
  const learner = new R.Learner();
  // ZERO is outside STARTER but is a valid authored source-world truth table.
  for (let i = 0; i < 4; i++) learner.observe(i, 0);
  assert.equal(learner.status(), "HOLD_OUT_OF_FAMILY");
  assert.equal(learner.candidates().length, 0);
  assert.equal(learner.prediction(2), null);
});
test("person-authored new operator is typed data and can repair out-of-family HOLD", () => {
  const learner = new R.Learner();
  // 0010 (row 2 only) is not among the initial eleven documented rules.
  for (const [row, bit] of [0, 0, 1, 0].entries()) learner.observe(row, bit);
  assert.equal(learner.status(), "HOLD_OUT_OF_FAMILY");
  learner.addOperator("PERSON_RULE", "0010", "person-explicit-review");
  assert.equal(learner.status(), "IDENTIFIED");
  assert.deepEqual(learner.candidates(), ["PERSON_RULE"]);
  assert.equal(learner.trace().events.at(-1).status, "USER_DEFINED_ONLY");
  assert.equal(learner.prediction(2), 1);
});
test("operator registry cannot replace source, duplicate methods, or run code", () => {
  const learner = new R.Learner();
  for (const [key, bits] of [
    ["XOR", "0010"], ["attempt();", "0010"], ["GOOD", "xyz1"],
    ["GOOD", "010101"], ["FAKE", "0110"]]) {
    assert.throws(() => learner.addOperator(key, bits));
  }
  assert.equal(learner.status(), "UNCERTAIN");
});
test("invalid inputs, modes and unearned revisions are rejected", () => {
  const learner = new R.Learner();
  for (const [row, value, mode] of [[4, 1, "OBSERVE"], [0, 2, "OBSERVE"],
     [0, 1, "EXECUTE"], [0, 1, "REPLACE"]]) {
    assert.throws(() => learner.observe(row, value, "person", mode));
  }
  assert.throws(() => R.output(17, 2));
  assert.throws(() => R.runSynthetic("MISSING"));
});
test("human probe is evaluated before explanation and source remains unclaimed", () => {
  const before = R.assessHuman(R.PRE, 0);
  const after = R.assessHuman(R.POST, 3);
  assert.equal(before.correct, true);
  assert.equal(after.correct, true);
  assert.equal(before.expectedRemaining, 2.6);
  assert.equal(after.expectedRemaining, 2.6);
});
test("trace is a copy; no agent model weights, live permissions or external side effects", () => {
  const learner = new R.Learner();
  learner.observe(1, 0, "person");
  learner.trace().events[0].value = 99;
  assert.equal(learner.latest().get(1), 0);
  assert.equal(typeof learner.invokeExternal, "undefined");
  assert.equal(typeof learner.trainWeights, "undefined");
});
let passed = 0;
for (const [name, fn] of tests) {
  fn(); passed++;
  process.stdout.write("PASS " + name + "\n");
}
process.stdout.write("RECIPROCAL-001 PASSED " + passed + " / " + tests.length + " tests\n");
