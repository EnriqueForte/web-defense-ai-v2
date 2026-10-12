"""Probe loopback TCP availability without connecting to existing services."""
import os
import socket


def probe_port(port):
    """Raise OSError if a new local listener cannot use this port.

    POSIX reuse permits the TIME_WAIT sockets left by reusable HTTP listeners.
    Windows reuse has different sharing semantics, so use exclusive binding.
    This is a preflight, not a reservation until the real server starts.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        if os.name == "nt":
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
            # Windows permits some wildcard/specific-address overlaps. A wildcard
            # exclusive reservation rejects those too; never listen on this socket.
            probe.bind(("0.0.0.0", port))
            return
        probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        probe.bind(("127.0.0.1", port))
        # Verify listener creation as well as address binding; accept no requests.
        probe.listen(1)
