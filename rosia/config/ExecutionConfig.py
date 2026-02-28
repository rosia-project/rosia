from pydantic import BaseModel
from datetime import datetime


class ExecutionConfig(BaseModel):
    trace: bool = False
    rerun_name: str = "rosia_rerun"
    rerun_recording_id: str = datetime.now().strftime("%Y%m%d_%H%M%S")
