import os
import io
import unittest
from unittest.mock import Mock, patch

from config import notifications


class EmailNotificationTransportTests(unittest.TestCase):
    def setUp(self):
        self.environment = {
            "EMAIL_REMITENTE": "sender@example.test",
            "EMAIL_PASSWORD": "lab-only-password",
            "EMAIL_DESTINATARIO": "receiver@example.test",
            "EMAIL_SMTP_SERVER": "127.0.0.1",
            "EMAIL_SMTP_PORT": "1025",
        }
        self.smtp = Mock()
        self.smtp.__enter__ = Mock(return_value=self.smtp)
        self.smtp.__exit__ = Mock(return_value=False)

    def test_starttls_remains_enabled_by_default(self):
        with patch.dict(os.environ, self.environment, clear=True), \
             patch("config.notifications.smtplib.SMTP", return_value=self.smtp) as smtp_factory, \
             patch("builtins.print"):
            self.assertTrue(notifications.enviar_email("Test", "Body"))

        smtp_factory.assert_called_once_with("127.0.0.1", 1025)
        self.smtp.starttls.assert_called_once_with()
        self.smtp.login.assert_called_once_with("sender@example.test", "lab-only-password")
        self.smtp.sendmail.assert_called_once()

    def test_starttls_can_be_disabled_explicitly_for_local_sink(self):
        with patch.dict(os.environ, {**self.environment, "EMAIL_SMTP_STARTTLS": "0"}, clear=True), \
             patch("config.notifications.smtplib.SMTP", return_value=self.smtp) as smtp_factory, \
             patch("builtins.print"):
            self.assertTrue(notifications.enviar_email("Test", "Body"))

        smtp_factory.assert_called_once_with("127.0.0.1", 1025)
        self.smtp.starttls.assert_not_called()
        self.smtp.login.assert_called_once_with("sender@example.test", "lab-only-password")
        self.smtp.sendmail.assert_called_once()

    def test_local_sink_can_accept_mailpit_without_authentication(self):
        environment = {**self.environment, "EMAIL_PASSWORD": "", "EMAIL_SMTP_STARTTLS": "0"}
        with patch.dict(os.environ, environment, clear=True), \
             patch("config.notifications.smtplib.SMTP", return_value=self.smtp), \
             patch("builtins.print"):
            self.assertTrue(notifications.enviar_email("Test", "Body"))

        self.smtp.login.assert_not_called()
        self.smtp.sendmail.assert_called_once()

    def test_non_loopback_sink_requires_a_password(self):
        environment = {
            **self.environment,
            "EMAIL_PASSWORD": "",
            "EMAIL_SMTP_SERVER": "smtp.example.test",
        }
        with patch.dict(os.environ, environment, clear=True), \
             patch("config.notifications.smtplib.SMTP") as smtp_factory, \
             patch("builtins.print"):
            self.assertFalse(notifications.enviar_email("Test", "Body"))

        smtp_factory.assert_not_called()

    def test_local_email_success_does_not_depend_on_console_emoji_encoding(self):
        output = io.TextIOWrapper(io.BytesIO(), encoding="cp1252")
        with patch.dict(os.environ, self.environment, clear=True), \
             patch("config.notifications.smtplib.SMTP", return_value=self.smtp), \
             patch("sys.stdout", output):
            self.assertTrue(notifications.enviar_email("Test", "Body"))

        self.smtp.sendmail.assert_called_once()

    def test_starttls_cannot_be_disabled_for_non_loopback_host(self):
        environment = {
            **self.environment,
            "EMAIL_SMTP_SERVER": "smtp.example.test",
            "EMAIL_SMTP_STARTTLS": "0",
        }
        with patch.dict(os.environ, environment, clear=True), \
             patch("config.notifications.smtplib.SMTP", return_value=self.smtp), \
             patch("builtins.print"):
            self.assertTrue(notifications.enviar_email("Test", "Body"))

        self.smtp.starttls.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
