"""Own only newly spawned processes: a Windows Job or separate POSIX sessions."""
import ctypes
import os
from pathlib import Path
import signal
import subprocess
import sys
import time


class WindowsJob:
    def __init__(self):
        from ctypes import wintypes as w

        class Basic(ctypes.Structure):
            _fields_ = [("user_time", ctypes.c_int64), ("job_time", ctypes.c_int64),
                        ("flags", w.DWORD), ("min_set", ctypes.c_size_t), ("max_set", ctypes.c_size_t),
                        ("active", w.DWORD), ("affinity", ctypes.c_size_t),
                        ("priority", w.DWORD), ("scheduling", w.DWORD)]

        class Extended(ctypes.Structure):
            _fields_ = [("basic", Basic), ("io", ctypes.c_uint64 * 6),
                        ("memory", ctypes.c_size_t * 4)]

        self.api = ctypes.WinDLL("kernel32", use_last_error=True)
        for name, argtypes, restype in (
            ("CreateJobObjectW", [ctypes.c_void_p, w.LPCWSTR], w.HANDLE),
            ("SetInformationJobObject", [w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD], w.BOOL),
            ("AssignProcessToJobObject", [w.HANDLE, w.HANDLE], w.BOOL),
            ("CloseHandle", [w.HANDLE], w.BOOL),
        ):
            function = getattr(self.api, name)
            function.argtypes, function.restype = argtypes, restype
        self.handle = self.api.CreateJobObjectW(None, None)
        if not self.handle:
            raise OSError("No se pudo crear el grupo de procesos")
        info = Extended()
        info.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not self.api.SetInformationJobObject(self.handle, 9, ctypes.byref(info), ctypes.sizeof(info)):
            self.close()
            raise OSError("No se pudo configurar el cierre de procesos")

    def assign(self, process):
        if not self.api.AssignProcessToJobObject(self.handle, int(process._handle)):
            raise OSError("No se pudo asociar el proceso al lanzador")

    def close(self):
        if self.handle:
            self.api.CloseHandle(self.handle)
            self.handle = None


class ProcessOwner:
    def __init__(self):
        self.processes = []
        self.job = WindowsJob() if os.name == "nt" else None

    def spawn(self, command, *, cwd, env, log):
        # A base Python gate avoids the Windows venv redirector spawning before assignment.
        gate = Path(__file__).with_name("owned_process.py")
        command = [getattr(sys, "_base_executable", sys.executable), "-B", str(gate), *command]
        options = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if self.job else {"start_new_session": True}
        process = subprocess.Popen(command, cwd=cwd, env=env, stdin=subprocess.PIPE,
                                   stdout=log, stderr=subprocess.STDOUT, **options)
        self.processes.append(process)
        try:
            if self.job:
                self.job.assign(process)
            process.stdin.write(b"1")
            process.stdin.flush()
        except BaseException:
            process.kill()  # gate has not launched the application if assignment failed
            process.wait(timeout=5)
            raise
        finally:
            process.stdin.close()
        return process

    def close(self):
        if self.job:
            self.job.close()  # Includes descendants even if their immediate parent already exited.
        else:
            for process in self.processes:
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
            deadline = time.monotonic() + 3
            for process in self.processes:
                try:
                    process.wait(timeout=max(.01, deadline - time.monotonic()))
                except subprocess.TimeoutExpired:
                    pass
            for process in self.processes:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        for process in self.processes:
            process.wait(timeout=5)
        self.processes.clear()
