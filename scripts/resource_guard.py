"""Resource guard for evaluation fan-out.

Limits set by the user: CPU and memory must stay below 80 percent. The GPU has no limit.
A new process starts only when memory use and CPU load are both below the start threshold, which sits under
the limit to leave room for the process that is about to load the connectome. A hard process cap remains.

History: an earlier pilot launched 28 evaluation processes at once, memory and CPU reached 100 percent and the
machine restarted. Use run_limited for every fan-out.
"""
import ctypes, os, subprocess, time

LIMIT_PERCENT = 80          # user limit for CPU and memory
START_BELOW_PERCENT = 65    # start a new process only below this, because a loading process adds load
MAX_PARALLEL = 8
STAGGER_SECONDS = 20        # the connectome load is the memory and CPU peak
THREADS = "2"                # per process; unrestricted numerical libraries use every core and exceeded the CPU limit
ENV = {**os.environ, "OMP_NUM_THREADS": THREADS, "MKL_NUM_THREADS": THREADS, "OPENBLAS_NUM_THREADS": THREADS, "NUMEXPR_NUM_THREADS": THREADS}


class _Memory(ctypes.Structure):
    _fields_ = [('length', ctypes.c_ulong), ('load', ctypes.c_ulong), ('total', ctypes.c_ulonglong),
                ('avail', ctypes.c_ulonglong), ('tpf', ctypes.c_ulonglong), ('apf', ctypes.c_ulonglong),
                ('tv', ctypes.c_ulonglong), ('av', ctypes.c_ulonglong), ('ae', ctypes.c_ulonglong)]


def memory_used_percent():
    s = _Memory(); s.length = ctypes.sizeof(s)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(s))
    return 100.0 * (1.0 - s.avail / s.total)


def _times():
    idle, kernel, user = (ctypes.c_ulonglong() for _ in range(3))
    ctypes.windll.kernel32.GetSystemTimes(ctypes.byref(idle), ctypes.byref(kernel), ctypes.byref(user))
    return idle.value, kernel.value + user.value


def cpu_percent(interval=1.0):
    i0, t0 = _times(); time.sleep(interval); i1, t1 = _times()
    total = t1 - t0
    return 100.0 * (1.0 - (i1 - i0) / total) if total else 0.0


def can_start():
    return memory_used_percent() < START_BELOW_PERCENT and cpu_percent() < START_BELOW_PERCENT


def run_limited(commands, max_parallel=MAX_PARALLEL):
    """Run commands under the CPU and memory limits. Returns when all finish; raises if any failed."""
    pending, running, failed = list(commands), [], []
    last_start = 0.0
    while pending or running:
        still = []
        for cmd, proc in running:
            if proc.poll() is None:
                still.append((cmd, proc))
            elif proc.returncode != 0:
                failed.append(cmd)
        running = still
        if (pending and len(running) < max_parallel and time.time() - last_start >= STAGGER_SECONDS
                and (not running or can_start())):
            cmd = pending.pop(0)
            running.append((cmd, subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=ENV)))
            last_start = time.time()
        time.sleep(2)
    if failed:
        raise RuntimeError(f'{len(failed)} evaluation commands failed')
