# Rosia: Reproducible Robotic Middleware

## Install
```bash
pip install rosia
```

Alternatively, you can install from source:

```bash
git clone https://github.com/rosia-project/rosia.git
cd rosia
pip install -e .
```

## Hello World


```python
from rosia import InputPort, OutputPort, reaction, Node, Application
from rosia import log

@Node
class Greeter:
    output = OutputPort[str]()
    def start(self):
        self.output("Hello, World!")

@Node
class Printer:
    message = InputPort[str]()
    @reaction([message])
    def print_message(self):
        log.info(self.message)

if __name__ == "__main__":
    app = Application()
    greeter = app.create_node(Greeter())
    printer = app.create_node(Printer())
    greeter.output >>= printer.message
    app.execute()
```

## Contributing
### Install Dev Dependencies
```bash
pip install --group dev .
```

### Install Pre-commit Hooks
```bash
pre-commit install --hook-type commit-msg --hook-type pre-push --hook-type pre-commit
pre-commit run --all-files
```
Code is automatically formatted before committing. Commit messages should follow conventional commit.

### Distribution Archives
```bash
python -m build
python -m twine upload dist/*
```