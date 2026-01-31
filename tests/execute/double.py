from rosia.execute import ExecutorController


class NumberDoubler:
    """A simple class that can double numbers."""

    def __init__(self):
        pass

    def double(self, number: int) -> int:
        """Double the given number."""
        return number * 2


def test_double_number_remotely():
    """Test that we can double a number using ExecutorController."""
    # Create an executor controller for the NumberDoubler class
    controller = ExecutorController(NumberDoubler)

    # Initialize the instance remotely
    controller.call("__init__")

    # Test doubling various numbers
    assert controller.call("double", 5) == 10
    assert controller.call("double", 0) == 0
    assert controller.call("double", -3) == -6
    assert controller.call("double", 100) == 200

    # Clean up
    controller.remote_process.terminate()
    controller.remote_process.join()


if __name__ == "__main__":
    test_double_number_remotely()
    print("All tests passed!")
