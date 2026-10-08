"""Offline tests for honest product-specific interest metrics."""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
from public_interest import summarise


class PublicInterestTests(unittest.TestCase):
    def setUp(self):
        self.repo = {"private": False, "owner": {"login": "PGhannmmn"}}
        self.issue = {"number": 1, "state": "open", "comments": 3}

    def test_excludes_owner_and_bots(self):
        comments = [
            {"user": {"login": "PGhannmmn", "type": "User"}},
            {"user": {"login": "helper[bot]", "type": "Bot"}},
            {"user": {"login": "developer1", "type": "User"}, "created_at": "2026-10-09T10:00:00Z"},
            {"user": {"login": "developer1", "type": "User"}, "created_at": "2026-10-10T10:00:00Z"},
            {"user": {"login": "developer2", "type": "User"}, "created_at": "2026-10-11T10:00:00Z"},
        ]
        result = summarise("PGhannmmn/base-usdc-mcp-tools", self.repo, self.issue, comments)
        self.assertEqual(result["potential_external_comments"], 3)
        self.assertEqual(result["potential_external_commenters"], 2)
        self.assertEqual(result["last_external_comment_at"], "2026-10-11T10:00:00Z")
        self.assertIsNone(result["actual_downloads"])
        self.assertIsNone(result["verified_demand"])

    def test_zero_comment_baseline(self):
        result = summarise("PGhannmmn/base-usdc-mcp-tools", self.repo, self.issue, [])
        self.assertEqual(result["potential_external_comments"], 0)
        self.assertEqual(result["potential_external_commenters"], 0)
        self.assertIsNone(result["last_external_comment_at"])

    def test_private_repo_fails_closed(self):
        with self.assertRaises(ValueError):
            summarise("x/y", {"private": True, "owner": {"login": "x"}}, self.issue, [])

    def test_wrong_issue_fails_closed(self):
        with self.assertRaises(ValueError):
            summarise("x/y", self.repo, {"number": 99}, [])

    def test_empty_unknown_user_not_counted(self):
        comments = [{"user": None}, {"user": {}}, {"user": {"login": ""}}]
        result = summarise("x/y", self.repo, self.issue, comments)
        self.assertEqual(result["potential_external_commenters"], 0)


if __name__ == "__main__":
    unittest.main()
