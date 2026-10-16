"""Fixture planning and network boundary checks; no Docker or SMTP here."""
import contextlib
import io
from unittest import TestCase
from unittest.mock import patch

from scripts import check_mailpit_compat as compat


class MailpitCompatibilityTests(TestCase):
    def test_plan_never_contacts_docker_or_network(self):
        with patch("sys.argv", ["check_mailpit_compat.py"]), \
             patch.object(compat, "docker", side_effect=AssertionError("No Docker")), \
             patch.object(compat, "build_opener", side_effect=AssertionError("No HTTP")), \
             contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(compat.main(), 0)
        self.assertIn('"containers_started": false', output.getvalue())

    def test_only_one_explicit_loopback_binding_is_accepted(self):
        valid = {"8025/tcp": [{"HostIp": "127.0.0.1", "HostPort": "49152"}]}
        self.assertEqual(compat.loopback_port(valid, "8025"), 49152)
        for values in ([], [{"HostIp": "0.0.0.0", "HostPort": "49152"}],
                       [{"HostIp": "127.0.0.1", "HostPort": "0"}],
                       [*valid["8025/tcp"], {"HostIp": "::", "HostPort": "49152"}]):
            with self.subTest(values=values), self.assertRaises(ValueError):
                compat.loopback_port({"8025/tcp": values}, "8025")

    def test_unreviewed_reference_is_rejected_before_any_docker_call(self):
        with patch.object(compat, "docker", side_effect=AssertionError("No Docker")):
            with self.assertRaisesRegex(ValueError, "unreviewed_fixture_reference"):
                compat.run_case("candidate-mailpit", "unreviewed:latest", None, None)
