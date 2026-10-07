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

        smtp_factory.assert_called_once_with("127.0.0.1", 1025, timeout=10.0)
        self.smtp.starttls.assert_called_once_with()
        self.smtp.login.assert_called_once_with("sender@example.test", "lab-only-password")
        self.smtp.sendmail.assert_called_once()

    def test_starttls_can_be_disabled_explicitly_for_local_sink(self):
        with patch.dict(os.environ, {**self.environment, "EMAIL_SMTP_STARTTLS": "0"}, clear=True), \
             patch("config.notifications.smtplib.SMTP", return_value=self.smtp) as smtp_factory, \
             patch("builtins.print"):
            self.assertTrue(notifications.enviar_email("Test", "Body"))

        smtp_factory.assert_called_once_with("127.0.0.1", 1025, timeout=10.0)
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


    def test_smtp_timeouts_are_finite_and_bounded(self):
        for configured, expected in (("4", 4.0), ("1000", 60.0), ("0", 10.0),
                                     ("-2", 10.0), ("nan", 10.0), ("inf", 10.0), ("invalid", 10.0)):
            with self.subTest(value=configured), \
                 patch.dict(os.environ, {**self.environment, "EMAIL_SMTP_TIMEOUT_SECONDS": configured}, clear=True), \
                 patch.object(notifications.smtplib, "SMTP", return_value=self.smtp) as factory, \
                 patch("builtins.print"):
                self.assertTrue(notifications.enviar_email("Synthetic", "Synthetic"))
                self.assertEqual(factory.call_args.kwargs["timeout"], expected)

    def test_stalled_connect_tls_login_send_or_quit_returns_false(self):
        for stage in ("connect", "starttls", "login", "sendmail", "quit"):
            with self.subTest(stage=stage):
                smtp = Mock()
                smtp.__enter__ = Mock(return_value=smtp)
                smtp.__exit__ = Mock(return_value=False)
                if stage == "quit":
                    smtp.__exit__.side_effect = TimeoutError("synthetic-private-detail")
                elif stage != "connect":
                    getattr(smtp, stage).side_effect = TimeoutError("synthetic-private-detail")
                with patch.dict(os.environ, self.environment, clear=True), \
                     patch.object(notifications.smtplib, "SMTP", return_value=smtp,
                                  side_effect=TimeoutError("synthetic-private-detail") if stage == "connect" else None), \
                     patch("sys.stdout", new_callable=io.StringIO) as output:
                    self.assertFalse(notifications.enviar_email("Synthetic", "Synthetic"))
                self.assertNotIn("synthetic-private-detail", output.getvalue())

    def test_invalid_port_fails_before_connect(self):
        for value in ("invalid", "0", "65536"):
            with patch.dict(os.environ, {**self.environment, "EMAIL_SMTP_PORT": value}, clear=True), \
                 patch.object(notifications.smtplib, "SMTP") as factory, patch("builtins.print"):
                self.assertFalse(notifications.enviar_email("Synthetic", "Synthetic"))
                factory.assert_not_called()


class TelegramDiagnosticTests(unittest.TestCase):
    def test_transport_errors_never_print_url_credentials_or_payload(self):
        token = "synthetic-bot-token"
        detail = f"https://api.telegram.org/bot{token}/sendMessage; private-message"
        with patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": token, "TELEGRAM_CHAT_ID": "synthetic-chat"}, clear=True), \
             patch.object(notifications.requests, "post", side_effect=RuntimeError(detail)), \
             patch("sys.stdout", new_callable=io.StringIO) as output:
            self.assertFalse(notifications.enviar_telegram("private-message"))
        self.assertIn("fallo de transporte", output.getvalue())
        for secret in (token, "synthetic-chat", "private-message", detail):
            self.assertNotIn(secret, output.getvalue())

    def test_http_errors_log_only_status_code(self):
        response = Mock(status_code=401, text="synthetic-secret-response")
        with patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "synthetic-token", "TELEGRAM_CHAT_ID": "synthetic-chat"}, clear=True), \
             patch.object(notifications.requests, "post", return_value=response), \
             patch("sys.stdout", new_callable=io.StringIO) as output:
            self.assertFalse(notifications.enviar_telegram("synthetic-message"))
        self.assertIn("HTTP 401", output.getvalue())
        self.assertNotIn(response.text, output.getvalue())

    def test_success_keeps_existing_transport_contract(self):
        with patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "synthetic-token", "TELEGRAM_CHAT_ID": "synthetic-chat"}, clear=True), \
             patch.object(notifications.requests, "post", return_value=Mock(status_code=200)) as send, \
             patch("builtins.print"):
            self.assertTrue(notifications.enviar_telegram("synthetic-message"))
        self.assertEqual(send.call_args.kwargs["timeout"], 10)
        self.assertEqual(send.call_args.kwargs["json"]["text"], "synthetic-message")


if __name__ == "__main__":
    unittest.main()
