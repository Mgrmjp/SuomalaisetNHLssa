"""A committed data update is not considered published until the live marker matches."""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests
import check_deployment


class DeploymentTests(unittest.TestCase):
    def response(self, metadata):
        response = Mock()
        response.json.return_value = metadata
        return response

    def test_failed_publish_retries_when_the_data_commit_is_already_saved(self):
        with patch.object(check_deployment.requests, "get", return_value=self.response({"revision": "older"})):
            self.assertTrue(check_deployment.needs_deployment("https://example.invalid/deployment.json", "saved-data-commit"))

    def test_matching_live_revision_skips_rebuild(self):
        with patch.object(check_deployment.requests, "get", return_value=self.response({"revision": "current"})) as getter:
            self.assertFalse(check_deployment.needs_deployment("https://example.invalid/deployment.json", "current"))
        self.assertEqual(getter.call_args.kwargs["timeout"], 15)
        self.assertIn("t", getter.call_args.kwargs["params"])

    def test_missing_or_invalid_marker_retries(self):
        for metadata in ({}, [], None):
            with self.subTest(metadata=metadata), patch.object(
                check_deployment.requests, "get", return_value=self.response(metadata)
            ):
                self.assertTrue(check_deployment.needs_deployment("https://example.invalid/deployment.json", "current"))

    def test_unreachable_live_site_does_not_suppress_a_deployment(self):
        with patch.object(check_deployment.requests, "get", side_effect=requests.Timeout("Unavailable")):
            self.assertTrue(check_deployment.needs_deployment("https://example.invalid/deployment.json", "current"))

    def test_written_artifact_is_recognized_after_successful_publish(self):
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / "build/data/deployment.json"
            check_deployment.write_deployment_marker(marker, "current")
            with patch.object(check_deployment.requests, "get", return_value=self.response(json.loads(marker.read_text()))):
                self.assertFalse(check_deployment.needs_deployment("https://example.invalid/deployment.json", "current"))

    def test_actions_output_requests_retry_without_a_new_data_update(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "output"
            with patch.object(sys, "argv", ["check_deployment.py", "--check-url", "https://example.invalid/deployment.json"]), patch.dict(
                os.environ, {"GITHUB_OUTPUT": str(output)}
            ), patch.object(check_deployment, "source_revision", return_value="current"), patch.object(
                check_deployment.requests, "get", return_value=self.response({"revision": "older"})
            ):
                check_deployment.main()
            self.assertEqual(output.read_text(), "needs_deployment=true\n")


if __name__ == "__main__":
    unittest.main()
