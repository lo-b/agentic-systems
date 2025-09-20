# Exploration of _agentic systems_

Agentic systems exploration using LangChain and LangGraph.

## Requirements

- docker 🐋: to run containerized workloads
  - [macOS](https://docs.docker.com/desktop/setup/install/mac-install/)
  - [Windows](https://docs.docker.com/desktop/setup/install/windows-install/)
- ollama 🦙: run local LLM models with ease (using docker)
  - [macOS](https://ollama.com/download/mac)
  - [Windows](https://ollama.com/download/windows)
- uv ☀️: a Python package and project manager.
  - [macOS](https://docs.astral.sh/uv/getting-started/installation/#__tabbed_1_1)
  - [Windows](https://docs.astral.sh/uv/getting-started/installation/#__tabbed_1_2)

<!-- TODO: extend/replace venv info with IDE setup-->
<!-- TODO: install python necessary? -->

## Using virtual environment (venv)

Depending on your workflow you might have to manually activate the python venv.

Run `uv sync` to update/sync the project environment. A `.venv` dir is created if it does not exist and package are
installed here.

Then run the command appropriate for your OS below, which will activate the environment.

### macOS

```bash
source .venv/bin/activate
```

### Windows

```powershell
.venv\Scripts\activate
```

## Getting started

Running any python file/script is as simple as `uv run <file_name>`:

```bash
uv run main.py
```

## Installing Packages

> ⚠️ Use `uv` for all python related tasks. I.e. _refrain from using the `python` command directly_.

Use the `uv add <pkg_name(s)>` command to install additional packages:

```bash
uv add langchain
```

## Running tests

Run a module its tests using `uv run python -m unittest <test_file>`:

```bash
uv run python -m unittest module_01/runnables_test.py -v
```
