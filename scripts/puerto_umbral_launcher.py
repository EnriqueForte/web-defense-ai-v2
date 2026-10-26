"""Lifecycle for the explicitly selected, bundled local laboratory.

Never starts scenarios, model jobs, periodic monitoring or unrelated containers.
"""
from pathlib import Path
import subprocess
import sys


class PuertoUmbralSession:
    def __init__(self, root):
        self.root = Path(root) / "labs" / "puerto_umbral"
        self.cli = self.root / "labctl.py"
        self.claimed = False

    def command(self, action):
        return [sys.executable, "-B", str(self.cli), action]

    def preflight(self):
        if not self.cli.is_file():
            raise ValueError("Falta labs/puerto_umbral en este checkout. Actualiza el proyecto completo.")
        result = subprocess.run(self.command("preflight"), cwd=self.root,
                                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=90)
        if result.returncode:
            raise ValueError("Puerto Umbral no está preparado. Comprueba Docker/Compose y que no haya otra sesión del laboratorio en marcha.\n" + result.stderr[-1200:])

    def prepare(self, owner, *, env, log):
        self.claimed = True
        process = owner.spawn(self.command("prepare"), cwd=self.root, env=env, log=log)
        try:
            code = process.wait()
        finally:
            # Completed groups must not be signalled again after a PID is recycled.
            if process.poll() is not None:
                owner.processes.remove(process)
        if code:
            raise RuntimeError("Puerto Umbral no pudo prepararse. Revisa puerto-prepare.log; no se inician escenarios.")

    def spawn_control(self, owner, *, env, log):
        return owner.spawn(self.command("serve"), cwd=self.root, env=env, log=log)

    def close(self, log):
        if not self.claimed:
            return
        try:
            result = subprocess.run(self.command("stop"), cwd=self.root, stdout=log,
                                    stderr=subprocess.STDOUT, timeout=90)
            if result.returncode:
                print("Puerto Umbral no confirmó la parada. Revisa puerto-stop.log antes de volver a arrancar.", flush=True)
        except (OSError, subprocess.TimeoutExpired):
            print("Parada de Puerto Umbral no confirmada. Usa su labctl.py stop y conserva los datos.", flush=True)
