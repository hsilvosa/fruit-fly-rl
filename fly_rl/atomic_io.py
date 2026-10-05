"""Bounded retries for Windows readers temporarily blocking an atomic rename."""
import os
import time


def replace_file(source, destination):
    """Replace a closed temporary file without discarding the previous destination.

    Windows indexers, scanners, or readers may briefly deny a rename. Retry only
    those Windows error codes, for at most 170 ms of waiting. Persistent errors
    remain errors, and the temporary file is retained for diagnosis/recovery.
    This is atomic visibility on the same filesystem, not a power-loss guarantee.
    """
    delays = (.02, .05, .10)
    for attempt in range(len(delays)+1):
        try:
            os.replace(source, destination)
            return
        except OSError as error:
            if getattr(error, 'winerror', None) not in (5, 32, 33) or attempt == len(delays):
                raise
            time.sleep(delays[attempt])
