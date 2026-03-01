import logging

from rich.console import Console

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
        self._console = Console(stderr=True)

    def __getstate__(self) -> dict:
        return {"_name": self._name, "_level": self._level}

    def __setstate__(self, state: dict) -> None:
        self._name = state["_name"]
        self._level = state["_level"]
        self._console = Console(stderr=True)

    def _log(self, level: int, msg: str) -> None:
        if self._level <= level:
            style = _LEVEL_STYLES.get(level, "")
            self._console.print(
                f"[{style}]\\[{self._name}] {msg}[/{style}]", highlight=False
            )

    def set_level(self, level: int) -> None:
        self._level = level

    def set_logger(self, logger: "Logger") -> None:
        self._name = logger._name
        self._level = logger._level

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
