# Exploration of _agentic systems_

Agentic systems exploration using LangChain and LangGraph.

## Requirements

- uv ☀️: a Python package and project manager.
  - [macOS](https://docs.astral.sh/uv/getting-started/installation/#__tabbed_1_1)
  - [Windows](https://docs.astral.sh/uv/getting-started/installation/#__tabbed_1_2)
- docker 🐋: to run containerized workloads
  - [macOS](https://docs.docker.com/desktop/setup/install/mac-install/)
  - [Windows](https://docs.docker.com/desktop/setup/install/windows-install/)
- ollama 🦙: run local LLM models with ease (using docker)
  - [macOS](https://ollama.com/download/mac)
  - [Windows](https://ollama.com/download/windows)

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

Example file content (placeholders shown):

```text
# LangSmith (tracing/monitoring)
LANGSMITH_PROJECT=agentic-systems
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=lsv2_xxx_your_langsmith_api_key
# Uncomment env var below when using an EU west data region
# LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com

# Qdrant (vector database)
QDRANT_CLUSTER_ENDPOINT=https://your-cluster-id.your-region-0.gcp.cloud.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key

# Azure AI Inference
AZURE_AI_ENDPOINT=https://agentic-systems-resource.services.ai.azure.com/models
AZURE_AI_CREDENTIAL=azure-ai-foundry-api-key

# GitHub (for the custom MCP GitHub server)
GITHUB_SERVICE_URL=https://api.github.com
GITHUB_OWNER=your-github-username-or-org
GITHUB_PERSONAL_ACCESS_TOKEN=github_pat_xxx_your_token
GITHUB_API_VERSION=2022-11-28

# Webhook secret
GITHUB_WEBHOOK_SECRET=my-secret

# GitHub App (bot) creds
GITHUB_APP_CLIENT_ID=app-client-id
GITHUB_APP_INSTALL_ID=12345678
GITHUB_APP_PEM_PATH="/path/to/my.pem"
GITHUB_APP_JWT=eyJ...
GITHUB_APP_ACCESS_TOKEN=ghs_cj...

# Webhook env settings
VALIDATE_SIG=true
WEBHOOK_PORT=8080
```

#### variables overview

| Variable                       | Description                                                               |
| ------------------------------ | ------------------------------------------------------------------------- |
| `LANGSMITH_PROJECT`            | Project name for LangSmith tracing and monitoring                         |
| `LANGSMITH_TRACING`            | Enable/disable LangSmith tracing for debugging and observability          |
| `LANGSMITH_API_KEY`            | API key for authenticating with LangSmith services                        |
| `QDRANT_CLUSTER_ENDPOINT`      | URL endpoint for the Qdrant vector database cluster $^1$                  |
| `QDRANT_API_KEY`               | API key for authenticating with the Qdrant cluster                        |
| `AZURE_AI_ENDPOINT`            | Azure AI inference service endpoint URL                                   |
| `AZURE_AI_CREDENTIAL`          | Authentication credential for Azure AI $^2$                               |
| `GITHUB_SERVICE_URL`           | Base URL for the GitHub REST API                                          |
| `GITHUB_OWNER`                 | GitHub user/org whose repos are targeted                                  |
| `GITHUB_PERSONAL_ACCESS_TOKEN` | GitHub PAT used for authentication $^3$                                   |
| `GITHUB_API_VERSION`           | GitHub API version header value                                           |
| `GITHUB_WEBHOOK_SECRET`        | Secret used to verify the signature of incoming GitHub webhook payloads   |
| `GITHUB_APP_CLIENT_ID`         | Client ID of the GitHub App                                               |
| `GITHUB_APP_INSTALL_ID`        | Installation ID of the GitHub App for the target organization/repository  |
| `GITHUB_APP_PEM_PATH`          | Path to the private key (.pem file) of the GitHub App                     |
| `GITHUB_APP_JWT`               | Short-lived JWT generated from the GitHub App private key                 |
| `GITHUB_APP_ACCESS_TOKEN`      | Installation access token obtained using the JWT (refreshed periodically) |
| `VALIDATE_SIG`                 | Whether to validate HMAC signatures on incoming webhooks (`true`/`false`) |
| `WEBHOOK_PORT`                 | Port on which the webhook server listens (e.g., `8080`)                   |

> $^1$ Example: `https://871c0680-f6d1-41d9-be88-83c7cd7dcdad.europe-west3-0.gcp.cloud.qdrant.io`<br>
> $^2$ The `AZURE_INFERENCE_CREDENTIAL` is sent as a One-Time Password (OTP) via email<br>
> $^3$ Ensure the PAT is scoped to **Selected repositories** and has read+write access for the permission:
> `Contents`, `Issues`, `Metadata` (required) and `Pull requests`.

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
