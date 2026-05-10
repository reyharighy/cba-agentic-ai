<div id="top">

<div align="center">

# CONVERSATIONAL BUSINESS ANALYTICS

<em>Agentic AI for Interactive Business Analytics & Reasoning</em>

<em>Agent Service Edition (API-first)</em>

<em>Built with:</em>

<img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat&logo=Python&logoColor=white">
<img src="https://img.shields.io/badge/LangGraph-4B5563.svg?style=flat">
<img src="https://img.shields.io/badge/FastAPI-009688.svg?style=flat&logo=FastAPI&logoColor=white">
<img src="https://img.shields.io/badge/Groq-F55036.svg?style=flat&logo=Groq&logoColor=white">

<br>

<img src="https://img.shields.io/badge/Docker-2496ED.svg?style=flat&logo=Docker&logoColor=white">
<img src="https://img.shields.io/badge/PostgreSQL-4169E1.svg?style=flat&logo=PostgreSQL&logoColor=white">
<img src="https://img.shields.io/badge/SQLAlchemy-D71F00.svg?style=flat&logo=SQLAlchemy&logoColor=white">
<img src="https://img.shields.io/badge/E2B-000000.svg?style=flat&logo=E2B&logoColor=white">

</div>

---

## Overview

**Conversational Business Analytics (CBA)** is an experimental, open-source system for building **agentic, LLM-driven analytical workflows** that can reason, compute, observe results, and expose those capabilities via a **service-oriented API**.

This branch focuses on **serving the agent as a FastAPI-based backend**, intended to be consumed by one or more external user interfaces (e.g. Streamlit, web apps, notebooks).

The system enables:

- natural-language business queries,
- explicit analytical planning and execution,
- structured reasoning over relational data,
- observation-driven correction loops,
- and optional downstream visualization handled *outside* the agent service.

This project is a **research and learning platform** for agentic analytics — not a production BI tool.

---

## Project Status

⚠️ **Active Development**

This branch provides a **cleanly separated architecture**, with emphasis on:

- isolating the agent core from presentation concerns,
- serving agent capabilities via a stable HTTP API,
- improving observability and debuggability of agent workflows,
- and enabling multiple UI clients without coupling.

---

## Architecture: Binary-Responsibility Agent Graph

<div align="center">
  <img src="notebook/Binary-Responsibility%20Agent%20Graph.png" width="75%" alt="Binary-Responsibility Agent Graph" />
</div>

<br>

The system is built around a **Binary-Responsibility Agent Graph**, guided by the following principles:

### 1. Binary Branching

Each node has **at most two outgoing paths**, ensuring:
- localized decisions,
- predictable control flow,
- traceable failure modes.

### 2. Single Responsibility per Node

Each node performs **one clearly defined task**, such as:
- intent interpretation,
- context distillation,
- request classification,
- planning,
- execution,
- observation.

This limits prompt complexity and error propagation.

### 3. Explicit Planning–Execution–Observation Loops

Analytical reasoning follows a consistent loop:

- **Plan** — generate a constrained, structured plan  
- **Execute** — run code or actions in a controlled environment  
- **Observe** — validate semantic and functional correctness  

Failures trigger targeted correction loops rather than global retries.

### 4. Visualization as a Downstream Concern

Analytical correctness is established in the plan–execute–observe loop before the final conversational response. Optional visualization or chart generation as a separate post-processing step is **out of scope** for the current `main` orchestration graph; the agent focuses on grounded analytical explanation without an embedded visualization subgraph.

This keeps the execution graph smaller and easier to reason about for conversational business analytics.

---

## High-Level System Structure

```sh
.
├── agent/              # LangGraph-based agent and node definitions (core logic)
├── api/                # FastAPI service layer exposing the agent
├── context/            # Runtime context shared across agent nodes
├── docker_script/      # Database initialization & synthetic data seeding
├── language_model/     # LLM abstraction layer
├── memory/             # Conversational and short-term memory persistence
└── notebook/           # Agent graph export (Mermaid .txt, PNG) from get_mermaid_graph.ipynb
```

## Features

- 🧠 **Agentic Reasoning Pipeline**

  Intent → classification → planning → execution → observation.

- 📊 **Business Analytics Focus**  

  Supports descriptive, diagnostic, predictive, and inferential analysis.

- 🧾 **Structured LLM Outputs**

  Enforced via Pydantic schemas.

- 🧩 **LangGraph-based Orchestration**

  Explicit state transitions and execution control.

- 🐳 **Containerized Agent Service**

  FastAPI-based backend, UI-agnostic

- 🔒 **Sandboxed Code Execution**

  Analytical Python code runs in isolated E2B sandbox environments, separated from the OLTP data source.

- 🗃️ **External PostgreSQL Integration**
- 🧪 **Synthetic Data Seeding for Development**

## Running the Agent Service (Development)

### Prerequisites

You will need:

- **Docker**
- **Docker Compose**
- **Git**

No local Python installation is required if using Docker.

### Environment Setup

This project uses environment variables for configuration.

1. Copy the example file:

    ```sh
    cp .env.example .env
    ```

2. Fill in required values:

- API keys (Groq, E2B, optional LangSmith)
- PostgreSQL credentials (defaults work for Docker)
- `AGENT_API_PORT` (default: 8000)

### Start the Service

```sh
docker compose up --build
```

Once running, the agent API will be available to test with Swagger docs:

```sh
http://localhost:8000/docs#/
```

You can try using cURL to test the agent stream endpoint.

```sh
curl -X 'POST' \
  'http://localhost:8000/agent/stream' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "input": "What is the best-selling product in March 2024?"
}'
```

Health check endpoint:

```sh
GET /health
```

## Synthetic Data & External Database

This project depends on an external PostgreSQL database to simulate business data.

- Synthetic data is stored in docker_script/synthetic_data.csv
- The script external_database_factory.py:
  - creates the schema,
  - populates the database,
  - runs automatically on container startup if enabled.

Controlled via environment variable:

```env
ENABLE_EXTERNAL_DB_SEEDING=true
```

This allows:

- zero-setup onboarding for new users,
- reproducible analytical scenarios,
- safe experimentation without real business data.

## Notes for Contributors

- This project prioritizes clarity over cleverness
- Explicit state > implicit magic
- If something is ambiguous, it should probably be a schema
- If something is implicit, it should probably be a graph edge
- UI concerns do not belong in the agent core or service layer

<br>

---

<div align="left"><a href="#top">⬆ Return</a></div>

---
