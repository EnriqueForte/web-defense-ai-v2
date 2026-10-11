"""Preserve the explicit IPv6 loopback authority across Werkzeug host parsers."""
import re

from flask import Flask
from werkzeug.exceptions import SecurityError
from werkzeug.wsgi import get_host


IPV6_LOOPBACK_HOST = re.compile(r"\[::1\](?::([1-9][0-9]{0,4}))?")


class LocalHostFlask(Flask):
    def create_url_adapter(self, request):
        if request is None:
            return super().create_url_adapter(request)
        authority = request.environ.get("HTTP_HOST", "")
        if not authority.startswith("["):
            return super().create_url_adapter(request)

        # Werkzeug 3.1.8 compares the part before the first colon for both
        # authorities; 3.1.9 retains the IPv6 authority but still splits refs.
        # Neither behavior provides the exact IPv6 allowlist required here.
        match = IPV6_LOOPBACK_HOST.fullmatch(authority)
        trusted = self.config.get("TRUSTED_HOSTS") or ()
        if ("[::1]" not in trusted or match is None
                or (match[1] is not None and int(match[1]) > 65535)):
            raise SecurityError("Local host required.")

        # This request alone has already passed the strict allowlist. Preserve
        # its original authority for routing and external URLs. No global
        # configuration or incoming environ is rewritten.
        request.trusted_hosts = None
        request.host = get_host(request.environ)
        server_name = self.config["SERVER_NAME"]
        subdomain = None
        if self.url_map.host_matching:
            server_name = None
        elif not self.subdomain_matching:
            subdomain = self.url_map.default_subdomain or ""
        return self.url_map.bind_to_environ(
            request.environ, server_name=server_name, subdomain=subdomain
        )
