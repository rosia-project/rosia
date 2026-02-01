import logging
from rich.logging import RichHandler
from typing import TYPE_CHECKING
import rosia

FORMAT = "[%(name)s] %(message)s"
logging.basicConfig(
    level="WARNING", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)


class LogProxy:
    def __init__(self, default_logger):
        self.__dict__["_real_logger"] = default_logger

    def set_logger(self, new_logger):
        self.__dict__["_real_logger"] = new_logger

    def __getattr__(self, name):
        if name == "set_logger":
            return self.set_logger
        if name == "_real_logger":
            return self.__dict__["_real_logger"]
        return getattr(self.__dict__["_real_logger"], name)

    def __reduce__(self):
        """
        This is used to tell the pickler to find the logger by name in the new process.
        This solves inconsistency between `import rosia` and `from rosia import log` in the new process. They will get different objects if we don't do this.
        """
        return (getattr, (rosia, "log"))


log = logger = LogProxy(logging.getLogger("main"))

if TYPE_CHECKING:
    logger = logging.getLogger("main")
    log = logger
