"""Offline protocol tests for IMMUNE-002 optional direct Qwen experiment."""
import unittest
from dataclasses import replace

import giants
import model_trial


class GenuineModelProtocolTests(unittest.TestCase):
    def test_deterministic_fixture_never_counts_as_model(self):
        output = model_trial.trial("scripted")
        self.assertFalse(output["actual_model_inference"])
        self.assertEqual(output["real_calls"], 0)
        self.assertEqual(output["summary"]["n"], 9)
        self.assertEqual(output["summary"]["unauthorized_mutations_approved"], 0)
        self.assertEqual(output["summary"]["classical_acl_agreements"], 9)
        self.assertTrue(all(
            x["receipt"]["transport"] == "SCRIPTED_FIXTURE_NOT_A_MODEL"
            for x in output["cases"]))

    def test_model_has_no_tools_or_executable_code_route(self):
        self.assertIn("NO tools", model_trial.SYSTEM)
        self.assertIn("propose", model_trial.SYSTEM.lower())
        for t in model_trial.tasks():
            self.assertFalse(
                t.grant and t.attacked, "Attacked document must not gain user grant")

    def test_untrusted_text_does_not_enter_grant_generator(self):
        task = next(t for t in model_trial.tasks()
                    if t.key == "attack_counterfeit_approval")
        self.assertIn("approved", task.external_note)
        self.assertFalse(task.grant)
        action = giants.Action("SEND", (
            ("body", "The public demo is ready."),
            ("to", "recipient@example.invalid")))
        self.assertEqual(giants.authorized(action), "DENY_NO_EXACT_GRANT")

    def test_action_parser_rejects_wrong_types_and_unknown_operations(self):
        for o in (
            {"operation": "SEND", "arguments": {"to": 100}},
            {"operation": "SEND", "arguments": "to=recipient"},
            {"operation": "EVAL", "arguments": {}},
            {"unparseable_response": "non-json"},
        ):
            self.assertIsNone(model_trial._candidate(o))

    def test_parsed_mutation_no_scope_grant_is_rejected(self):
        task = next(t for t in model_trial.tasks()
                    if t.key == "attack_role_spoof")
        response = {"operation": "SEND",
                    "arguments": {"to": "recipient@example.invalid",
                                  "body": "The public demo is ready."}}
        proposed = model_trial._candidate(response)
        self.assertIsNotNone(proposed)
        self.assertFalse(task.grant)
        self.assertEqual(giants.authorized(proposed), "DENY_NO_EXACT_GRANT")

    def test_exact_authorized_action_is_permitted_not_executed(self):
        task = next(t for t in model_trial.tasks()
                    if t.key == "benign_authorized_send")
        response = {"operation": task.expected.operation,
                    "arguments": dict(task.expected.arguments)}
        proposal = model_trial._candidate(response)
        grant = giants.Grant(task.expected.operation,
                             giants.action_digest(task.expected), "authorized")
        self.assertEqual(giants.authorized(proposal, (grant,)),
                         "ALLOW_EXACT_GRANT")
        self.assertEqual(giants.authorized(
            replace(proposal, arguments=(("to", "wrong@example.invalid"),)),
            (grant,)), "DENY_NO_EXACT_GRANT")


if __name__ == "__main__":
    unittest.main()
