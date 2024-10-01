"""TODO."""

import time
from typing import Any, Callable

import rerun as rr


def rerun_log(func: Callable) -> Callable:
    """TODO."""
    import functools

    first = time.time()

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Callable:
        recording = rr.get_thread_local_data_recording()
        since_start = time.time() - first
        start = time.time()
        res = func(*args, **kwargs)
        time_spent = time.time() - start
        rr.set_time_seconds("bytewax", since_start, recording=recording)
        rr.log(
            f"bytewax/{func.__name__}",
            rr.Scalar(time_spent),
            recording=recording,
        )
        return res

    return wrapper
