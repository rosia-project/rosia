import rerun as rr
import rerun.blueprint as rrb


def send_blueprint() -> None:
    rr.send_blueprint(
        rrb.Blueprint(rrb.Spatial2DView(origin="/diagram", background=[255, 255, 255]))
    )
