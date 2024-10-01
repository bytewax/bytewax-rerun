from random import random
from time import sleep, time

import rerun as rr

from bytewax import operators as op
from bytewax.bytewax_rerun import RerunMessage, RerunSink
from bytewax.dataflow import Dataflow
from bytewax.testing import TestingSource

sink = RerunSink(
    application_id="metrics_app",
    recording_id="metrics_recording",
    operating_mode="connect",
    address="127.0.0.1:9876",
)

flow = Dataflow("rerun-test")
inp = op.input("inp", flow, TestingSource(list(range(100))))
inp = op.redistribute("scale", inp)


@sink.rerun_log(log_args=True)
def heavy_operation(item: int) -> RerunMessage:
    sleep(random())

    return RerunMessage(
        entity_path="message",
        entity=rr.Scalar(item + (random() * 2 - 1)),
        timeline="messages",
        time=time(),
    )


operated = op.map("operated", inp, heavy_operation)
op.output("to_rerun", operated, sink)
