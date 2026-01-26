# Brutus

This repository is for learning and experimentation. Use it only in environments you own or have explicit permission to test.

## Development

### Requirements
- Python 3

### Install

From the repository root:

```shell
python3 -m pip install -e .
```

(Optional) Use a virtual environment:

```shell
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

### Linting and formatting

```shell
python3 -m pip install -e ".[dev]"
ruff check .
ruff format .

# optional
pre-commit install
pre-commit run --all-files
```

### Sandbox (Docker)

Run a quick "does it work" check in a no-network container:

```shell
./sandbox.sh check
```

### Repository layout
- `src/` contains the Python modules.

### Security
If you believe you’ve found a security issue, see `SECURITY.md`.
