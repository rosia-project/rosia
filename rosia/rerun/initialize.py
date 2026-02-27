import rerun as rr

from rosia.rerun.blueprint import send_blueprint


def initialize(rerun_name: str, rerun_recording_id: str) -> None:
    rr.init(rerun_name, recording_id=rerun_recording_id, spawn=True)
    send_blueprint()
