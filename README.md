# Brutus

This repository is for learning and experimentation. Use it only in environments you own or have explicit permission to test.

## Development

### Requirements
- Python 3

### Install

From the repository root:

```shell
python3 -m pip install -r requirements.txt
```

(Optional) Use a virtual environment:

```shell
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### Linting and formatting

Install dev tooling:

```shell
python3 -m pip install -r requirements-dev.txt
```

Lint:

```shell
python3 -m ruff check .
```

Format:

```shell
python3 -m ruff format .
```

(Optional) Enable git pre-commit hooks:

```shell
pre-commit install
```

Run hooks on all files:

```shell
pre-commit run --all-files
```

### Repository layout
- `src/` contains the Python modules.

### Security
If you believe you’ve found a security issue, see `SECURITY.md`.
