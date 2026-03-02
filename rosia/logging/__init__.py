import logging

from rich.console import Console

from rosia.time import Time
from rosia.rerun import RerunManager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rosia.config import RerunConfig

_LEVEL_STYLES = {
    logging.DEBUG: "dim",
    logging.INFO: "bold blue",
    logging.WARNING: "bold yellow",
    logging.ERROR: "bold red",
    logging.CRITICAL: "bold white on red",
}


class Logger:
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    def __init__(self, name: str = "rosia") -> None:
        self._name = name
        self._level = logging.INFO
        self._console: Console | None = None
        self._trace = False
        self.logical_time = Time(0)
        self.physical_time = Time(0)

    @property
    def console(self) -> Console:
        if self._console is None:
            self._console = Console(stderr=True)
        return self._console

    def set_logical_time(self, logical_time: Time) -> None:
        self.logical_time = logical_time

    def set_physical_time(self, physical_time: Time) -> None:
        self.physical_time = physical_time

    def set_trace(self, trace: bool, rerun_config: "RerunConfig") -> None:
        self._trace = trace
        if self._trace:
            self._rerun_manager = RerunManager()
            self._rerun_manager.init(rerun_config)

    def _log(self, level: int, msg: str) -> None:
        if self._level <= level:
            style = _LEVEL_STYLES.get(level, "")
            self.console.print(
                f"[{style}]\\[{self._name}] {msg}[/{style}]", highlight=False
            )
        if self._trace:
            self._rerun_manager.trace(
                self._name, self.logical_time, self.physical_time, msg
            )

    def set_level(self, level: int) -> None:
        self._level = level

    def debug(self, msg: str) -> None:
        self._log(logging.DEBUG, msg)

    def info(self, msg: str) -> None:
        self._log(logging.INFO, msg)

    def warning(self, msg: str) -> None:
        self._log(logging.WARNING, msg)

    def error(self, msg: str) -> None:
        self._log(logging.ERROR, msg)

    def critical(self, msg: str) -> None:
        self._log(logging.CRITICAL, msg)
