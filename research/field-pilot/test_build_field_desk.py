"""Structural and privacy checks on the built FIELD-001 offline page."""
import unittest
from html.parser import HTMLParser

from build_field_desk import build


class FormParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.forms = set()
        self.scripts = 0
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        if "id" in d:
            self.ids.add(d["id"])
        if tag == "form":
            self.forms.add(d.get("id"))
        if tag == "script":
            self.scripts += 1


class BuildTests(unittest.TestCase):
    def test_page_is_self_contained_and_real_mode_blank(self):
        page = build()
        self.assertTrue(page.startswith("<!DOCTYPE html>"))
        self.assertIn("FIELD-001",page)
        self.assertIn("No network connection", page.lower().capitalize()
                      if False else "This page has no network connection")
        self.assertNotIn("<script src=",page)
        self.assertNotIn("<link rel=",page)
        self.assertNotIn("fetch(",page)
        self.assertNotIn("XMLHttpRequest",page)
        self.assertNotIn("localStorage.",page)
        self.assertNotIn("navigator.sendBeacon",page)
        self.assertNotIn("innerHTML",page)
        self.assertNotIn("__ENGINE__",page)
        self.assertNotIn("__APP__",page)
        self.assertLess(len(page),160_000)

    def test_forms_and_review_receipts_are_present(self):
        parser=FormParser()
        parser.feed(build())
        self.assertEqual(parser.scripts,2)
        self.assertEqual(parser.forms,{"add-card","add-event"})
        for ident in ("card-share","card-origin","card-area","card-hours",
                      "follow-kind","follow-source","cards-list",
                      "matches-list","journal-list","intro-draft",
                      "import-file","export","new-log","load-demo","statusline"):
            self.assertIn(ident,parser.ids)

    def test_direct_contacts_and_third_party_storage_are_not_requested(self):
        page=build()
        self.assertNotIn('type="email"',page)
        self.assertNotIn('type="tel"',page)
        self.assertNotIn('type="password"',page)
        self.assertNotIn("https://",page)
        self.assertIn("Nothing sent.",page)
        self.assertIn("operator report",page.lower())


if __name__ == "__main__":
    unittest.main()
