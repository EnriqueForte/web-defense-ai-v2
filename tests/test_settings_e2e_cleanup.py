"""Strict cleanup must allow asynchronous close but reject persistent listeners."""

import errno
from unittest import TestCase
from unittest.mock import Mock, patch

from scripts import check_settings_e2e as e2e


class SettingsE2ECleanupTests(TestCase):
    def test_transient_busy_port_is_rechecked_until_both_probes_pass(self):
        counts = {61001: 0, 61002: 0}

        def probe(port):
            counts[port] += 1
            if port == 61001 and counts[port] == 1:
                raise OSError(errno.EADDRINUSE, "synthetic transient close")

        clock = Mock()
        clock.monotonic.return_value = 0
        with patch.object(e2e, "probe_port", side_effect=probe), patch.object(e2e, "time", clock):
            e2e.wait_free_ports(tuple(counts))
        self.assertEqual(counts, {61001: 2, 61002: 2})
        clock.sleep.assert_called_once_with(.1)

    def test_persistent_busy_port_still_fails_within_the_deadline(self):
        clock = Mock()
        clock.monotonic.side_effect = [0, 10]
        with patch.object(e2e, "probe_port", side_effect=OSError(errno.EADDRINUSE, "synthetic listener")), \
             patch.object(e2e, "time", clock):
            with self.assertRaisesRegex(RuntimeError, "61001"):
                e2e.wait_free_ports((61001,))
        clock.sleep.assert_not_called()

    def test_unknown_permission_failure_is_not_retried_or_marked_free(self):
        clock = Mock()
        clock.monotonic.return_value = 0
        with patch.object(e2e, "probe_port", side_effect=OSError(errno.EACCES, "synthetic permission")), \
             patch.object(e2e, "time", clock):
            with self.assertRaises(OSError) as caught:
                e2e.wait_free_ports((61001,))
        self.assertEqual(caught.exception.errno, errno.EACCES)
        clock.sleep.assert_not_called()
