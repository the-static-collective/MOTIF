"""Structural and safety tests for unmerged source reuse; no Docker required."""
import io
import tarfile
import tempfile
import unittest
from pathlib import Path

from motif.branch_garden import HoldError, Pointer
from motif.branch_runner import _extract_safe_tar, plan, PROFILES
from motif.branch_source import _path_ok


class BranchSourceTests(unittest.TestCase):
    def test_source_path_never_escapes_original_commit(self):
        for bad in ("../README.md", "a/../b.py", "/etc/passwd", ".git/config",
                    "a//b.py", "README.exe", "-option.js"):
            self.assertFalse(_path_ok(bad), bad)
        self.assertTrue(_path_ok("experiments/reciprocal-002/two_doors.js"))

    def test_no_unreviewed_profile_is_executable(self):
        p = Pointer("experiment/reciprocal-004-ecosystem-crosswire-20261112",
                    "a" * 40)
        preview = plan("reciprocal-004-smoke", p)
        self.assertFalse(preview["execution_requested"])
        self.assertFalse(preview["automatic_merge"])
        self.assertIn("network:none", preview["constraints"])
        with self.assertRaises(HoldError):
            plan("reciprocal-004-smoke", Pointer("experiment/evil", "a" * 40))
        with self.assertRaises(HoldError):
            plan("arbitrary-command", p)

    def test_runner_fixes_command_and_source_paths(self):
        cfg = PROFILES["reciprocal-004-smoke"]
        self.assertTrue(all(c[0] == "node" for c in cfg["commands"]))
        self.assertTrue(all(p.startswith("experiments/reciprocal-") for p in cfg["paths"]))

    def _tar(self, name, payload=b"x", mode=0o644, type=tarfile.REGTYPE):
        stream = io.BytesIO()
        with tarfile.open(fileobj=stream, mode="w") as t:
            item = tarfile.TarInfo(name)
            item.size = len(payload) if type == tarfile.REGTYPE else 0
            item.mode = mode
            item.type = type
            t.addfile(item, io.BytesIO(payload) if type == tarfile.REGTYPE else None)
        return stream.getvalue()

    def test_tar_path_traversal_rejected(self):
        raw = self._tar("../steal.js")
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(HoldError):
                _extract_safe_tar(raw, Path(tmp), ("experiments/reciprocal-002",))

    def test_tar_links_rejected(self):
        raw = self._tar("experiments/reciprocal-002/escape", type=tarfile.SYMTYPE)
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(HoldError):
                _extract_safe_tar(raw, Path(tmp), ("experiments/reciprocal-002",))

    def test_normal_selected_source_materializes(self):
        raw = self._tar("experiments/reciprocal-002/test_engine.cjs", b"console.log('ok');")
        with tempfile.TemporaryDirectory() as tmp:
            _extract_safe_tar(raw, Path(tmp), ("experiments/reciprocal-002",))
            self.assertEqual((Path(tmp) / "experiments/reciprocal-002/test_engine.cjs").read_bytes(),
                             b"console.log('ok');")


if __name__ == "__main__":
    unittest.main()
