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

## Environment setup

#### VSCode setup

Follow the setup guide for [windows](https://code.visualstudio.com/docs/setup/windows) or
[macOS](https://code.visualstudio.com/docs/setup/mac).

Open the root folder of the git(hub) repository and install **_Workspace recommended extensions_**.

#### Accounts & services

Create free accounts (no credit card required) for the following services:

- **_LangSmith_**: monitoring & tracing for agents and LLM workflows
  1. [Sign up](https://smith.langchain.com/) with _Google, GitHub, Discord or email_
  2. Go to **_Settings_** > **_API Keys_**, create a new API key and store it somewhere

- **_Qdrant Cloud_**: vector database.
  1. [Sign up](https://login.cloud.qdrant.io/) with _Google, GitHub or email_
  2. Create a new cluster
  3. Store the auto generated API key
  4. Store the cluster its endpoint

#### sample `.env` file

```text
LANGSMITH_PROJECT=agentic-systems
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=...
QDRANT_CLUSTER_ENDPOINT=...
QDRANT_API_KEY=...
AZURE_INFERENCE_ENDPOINT=https://agentic-systems-resource.services.ai.azure.com/models
AZURE_INFERENCE_CREDENTIAL=...
```

#### variables overview

| Variable                     | Description                                                      |
| ---------------------------- | ---------------------------------------------------------------- |
| `LANGSMITH_PROJECT`          | Project name for LangSmith tracing and monitoring                |
| `LANGSMITH_TRACING`          | Enable/disable LangSmith tracing for debugging and observability |
| `LANGSMITH_API_KEY`          | API key for authenticating with LangSmith services               |
| `QDRANT_CLUSTER_ENDPOINT`    | URL endpoint for the Qdrant vector database cluster $^1$         |
| `QDRANT_API_KEY`             | API key for authenticating with the Qdrant cluster               |
| `AZURE_INFERENCE_ENDPOINT`   | Azure AI inference service endpoint URL                          |
| `AZURE_INFERENCE_CREDENTIAL` | Authentication credential for Azure AI $^2$                      |

> $^1$ example: `https://871c0680-f6d1-41d9-be88-83c7cd7dcdad.europe-west3-0.gcp.cloud.qdrant.io`<br>
> $^2$ The `AZURE_INFERENCE_CREDENTIAL` is sent as a One-Time Password (OTP) via email;

###

## Using Python virtual environment (venv)

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
