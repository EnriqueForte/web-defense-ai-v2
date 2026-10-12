"""Private subprocess gate: wait for ownership before executing any application."""
import os
import signal
import subprocess
import sys


if __name__ == "__main__":
    if sys.stdin.buffer.read(1) != b"1" or len(sys.argv) < 2:
        raise SystemExit(1)
    if os.name == "nt":
        # subprocess quotes Windows argument lists; CRT execv loses embedded spaces.
        signal.signal(signal.SIGBREAK, signal.SIG_IGN)
        raise SystemExit(subprocess.call(sys.argv[1:], env=os.environ))
    os.execvpe(sys.argv[1], sys.argv[1:], os.environ)
