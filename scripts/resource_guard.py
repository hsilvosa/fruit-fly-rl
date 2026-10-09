"""Resource guard for evaluation fan-out: a hard cap on concurrent processes and a free-memory check.

The earlier pilot launched 28 evaluation processes at once. Each loads the connectome, so memory and CPU
reached 100 percent and the machine restarted. Use run_limited for every fan-out.
"""
import subprocess, sys, time

MAX_PARALLEL = 3
MIN_FREE_RAM_MB = 8000


def free_ram_mb():
    import ctypes

    class Status(ctypes.Structure):
        _fields_ = [('length', ctypes.c_ulong), ('load', ctypes.c_ulong), ('total', ctypes.c_ulonglong),
                    ('avail', ctypes.c_ulonglong), ('tpf', ctypes.c_ulonglong), ('apf', ctypes.c_ulonglong),
                    ('tv', ctypes.c_ulonglong), ('av', ctypes.c_ulonglong), ('ae', ctypes.c_ulonglong)]
    s = Status(); s.length = ctypes.sizeof(s)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(s))
    return int(s.avail / 2 ** 20)


def run_limited(commands, max_parallel=MAX_PARALLEL, min_free_mb=MIN_FREE_RAM_MB):
    """Run commands with at most max_parallel at once; wait while free RAM is below the floor."""
    pending, running, failed = list(commands), [], []
    while pending or running:
        running = [(c, p) for c, p in running if p.poll() is None or (p.returncode != 0 and failed.append(c))]
        while pending and len(running) < max_parallel and free_ram_mb() >= min_free_mb:
            cmd = pending.pop(0)
            running.append((cmd, subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)))
            time.sleep(15)  # stagger start-up, because loading the connectome is the memory peak
        time.sleep(2)
    if failed:
        raise RuntimeError(f'{len(failed)} evaluation commands failed')
