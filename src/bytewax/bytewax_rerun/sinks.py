"""TODO."""

import time
from dataclasses import dataclass
from logging import getLogger
from pathlib import Path
from typing import Any, Callable, Iterable, Literal, Optional

import rerun as rr

from bytewax.outputs import DynamicSink, StatelessSinkPartition

logger = getLogger(__name__)

Component = rr.AsComponents | Iterable[rr.ComponentBatchLike]


@dataclass
class RerunMessage:
    """TODO."""

    entity_path: str | list[str]
    entity: Component

    # Optional timing info
    timeline: Optional[str]
    time: Optional[float]

    # Optional properties
    timeless: bool = False
    static: bool = False


class _RerunPartition(StatelessSinkPartition[RerunMessage]):
    def __init__(self, recording: rr.RecordingStream, worker_index: int) -> None:
        self.recording = recording
        self.worker_index = worker_index

    def write_batch(self, items: list[RerunMessage]) -> None:
        for item in items:
            if item.timeline is not None:
                assert (
                    item.time is not None
                ), "time info required in RerunMessage if timeline is set"
                # set_time_seconds sets the time for the specified timeline
                # only in the current thread, so we can safely use this in
                # a multi worker/thread/process scenario.
                rr.set_time_seconds(item.timeline, item.time, recording=self.recording)
            rr.log(
                f"worker{self.worker_index}/{item.entity_path}",
                item.entity,
                recording=self.recording,
                timeless=item.timeless,
                static=item.static,
            )


class RerunSink(DynamicSink):
    """TODO."""

    def __init__(
        self,
        application_id: str,
        recording_id: str,
        operating_mode: Literal["spawn", "connect", "save", "serve"] = "spawn",
        address: Optional[str] = None,
        save_dir: Optional[Path] = None,
    ) -> None:
        """TODO."""
        self.recording = rr.new_recording(
            application_id=application_id,
            recording_id=recording_id,
            make_thread_default=True,
            spawn=operating_mode == "spawn",
        )
        self.save_dir = None
        self.worker_index: None | int = None

        if operating_mode == "connect":
            assert (
                address is not None
            ), "Address must be set in operating_mode is 'connect'"
            print(address)
            rr.connect(addr=address, recording=self.recording)
        elif operating_mode == "save":
            assert (
                save_dir is not None
            ), "Path for save directory required if operating_mode is 'save'"
            # We save the dir locally and only call rr.save in the
            # `build` function so that each worker has its own file.
            assert save_dir.is_dir(), "save_dir must be a directory"
            self.save_dir = save_dir

            # Not sure why, but we also need to call `init` here even if
            # we already called `new_recording`, or this won't work.
            rr.init(application_id=application_id, recording_id=recording_id)
        elif operating_mode == "serve":
            rr.serve()
        elif operating_mode == "spawn":
            # Nothing to do
            pass
        else:
            msg = f"Invalid operating_mode: {operating_mode}"
            raise ValueError(msg)

    def build(
        self, step_id: str, worker_index: int, worker_count: int
    ) -> _RerunPartition:
        """TODO."""
        self.worker_index = worker_index
        if self.save_dir is not None:
            file_path = self.save_dir / f"recording-{worker_index}.rrd"
            if file_path.exists():
                msg = (
                    f"File {file_path} already exists, remove it "
                    "or choose another directory to save the file"
                )
                raise FileExistsError(msg)
            rr.save(path=file_path, recording=self.recording)
        return _RerunPartition(self.recording, worker_index)

    def rerun_log(
        self,
        log_args: bool = False,
        log_level: rr.TextLogLevel = rr.TextLogLevel.TRACE,
    ) -> Callable:
        """TODO."""

        def inner(func: Callable) -> Callable:
            """TODO."""
            import functools

            first = time.time()

            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Callable:
                if self.worker_index is None:
                    msg = "worker_index is not set, did you forget to use the sink?"
                    raise RuntimeError(msg)
                since_start = time.time() - first
                start = time.time()
                res = func(*args, **kwargs)
                time_spent = time.time() - start
                rr.set_time_seconds("bytewax", since_start, recording=self.recording)
                rr.log(
                    f"bytewax/worker{self.worker_index}/{func.__name__}",
                    rr.Scalar(time_spent),
                    recording=self.recording,
                )
                if log_args:
                    rr.log(
                        f"bytewax/worker{self.worker_index}/{func.__name__}",
                        rr.TextLog(
                            f"Args: {str(args)}, kwargs: {str(kwargs)}", level=log_level
                        ),
                        recording=self.recording,
                    )
                return res

            return wrapper

        return inner
