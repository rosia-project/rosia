import logging

from rosia.logging import Logger
from rosia.utils import ObjectProxy


def test_default_name():
    logger = Logger()
    assert logger._name == "rosia"


def test_custom_name():
    logger = Logger("MyNode")
    assert logger._name == "MyNode"


def test_default_level_is_info():
    logger = Logger()
    assert logger._level == logging.INFO


def test_set_level():
    logger = Logger()
    logger.set_level(Logger.WARNING)
    assert logger._level == logging.WARNING


def test_level_filtering(capsys):
    logger = Logger("test")
    logger.set_level(Logger.WARNING)

    logger.debug("hidden")
    logger.info("hidden")
    logger.warning("shown warning")
    logger.error("shown error")

    captured = capsys.readouterr()
    assert "hidden" not in captured.err
    assert "shown warning" in captured.err
    assert "shown error" in captured.err


def test_debug_level_shows_all(capsys):
    logger = Logger("test")
    logger.set_level(Logger.DEBUG)

    logger.debug("d")
    logger.info("i")
    logger.warning("w")

    captured = capsys.readouterr()
    assert "[test] d" in captured.err
    assert "[test] i" in captured.err
    assert "[test] w" in captured.err


def test_output_includes_name(capsys):
    logger = Logger("Printer_2")
    logger.set_level(Logger.DEBUG)
    logger.info("hello")

    captured = capsys.readouterr()
    assert "[Printer_2] hello" in captured.err


def test_all_log_methods(capsys):
    logger = Logger("all")
    logger.set_level(Logger.DEBUG)

    logger.debug("D")
    logger.info("I")
    logger.warning("W")
    logger.error("E")
    logger.critical("C")

    captured = capsys.readouterr()
    for letter in ["D", "I", "W", "E", "C"]:
        assert f"[all] {letter}" in captured.err


# --- ObjectProxy tests ---


def test_proxy_delegates_to_logger(capsys):
    proxy = ObjectProxy(Logger("node"))
    proxy.set_level(Logger.DEBUG)
    proxy.info("hello")

    captured = capsys.readouterr()
    assert "[node] hello" in captured.err


def test_proxy_set_target_swaps_underlying(capsys):
    original = Logger("old")
    proxy = ObjectProxy(original)

    new = Logger("new")
    new.set_level(Logger.DEBUG)
    proxy.set_target(new)
    proxy.debug("after swap")

    captured = capsys.readouterr()
    assert "[new] after swap" in captured.err


def test_proxy_set_level_forwards():
    inner = Logger()
    proxy = ObjectProxy(inner)
    proxy.set_level(Logger.ERROR)
    assert inner._level == logging.ERROR


def test_proxy_level_filtering(capsys):
    proxy = ObjectProxy(Logger("p"))
    proxy.set_level(Logger.WARNING)

    proxy.info("hidden")
    proxy.warning("visible")

    captured = capsys.readouterr()
    assert "hidden" not in captured.err
    assert "visible" in captured.err
