import pickle
import logging

from rosia.logging import Logger


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


def test_pickle_roundtrip(capsys):
    logger = Logger("PickleNode")
    logger.set_level(Logger.WARNING)

    restored = pickle.loads(pickle.dumps(logger))

    assert restored._name == "PickleNode"
    assert restored._level == logging.WARNING

    restored.info("should be hidden")
    restored.warning("should appear")

    captured = capsys.readouterr()
    assert "should be hidden" not in captured.err
    assert "should appear" in captured.err


def test_set_logger_copies_name_and_level():
    src = Logger("Source")
    src.set_level(Logger.ERROR)

    dst = Logger()
    dst.set_logger(src)

    assert dst._name == "Source"
    assert dst._level == logging.ERROR


def test_set_logger_output(capsys):
    src = Logger("Source")
    src.set_level(Logger.DEBUG)

    dst = Logger()
    dst.set_logger(src)
    dst.debug("from dst")

    captured = capsys.readouterr()
    assert "[Source] from dst" in captured.err


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
