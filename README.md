<div id="top">

<div align="center">

# CONVERSATIONAL BUSINESS ANALYTICS

<em>Agentic AI for Interactive Business Analytics & Reasoning</em>

<em>Built with:</em>

<img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat&logo=Python&logoColor=white">
<img src="https://img.shields.io/badge/LangChain-1C3C3C.svg?style=flat&logo=LangChain&logoColor=white">
<img src="https://img.shields.io/badge/LangGraph-4B5563.svg?style=flat">

<br>

<img src="https://img.shields.io/badge/Docker-2496ED.svg?style=flat&logo=Docker&logoColor=white">
<img src="https://img.shields.io/badge/PostgreSQL-4169E1.svg?style=flat&logo=PostgreSQL&logoColor=white">
<img src="https://img.shields.io/badge/SQLAlchemy-D71F00.svg?style=flat&logo=SQLAlchemy&logoColor=white">

</div>

---

## Overview

**Conversational Business Analytics (CBA)** is an experimental, open-source system for building **agentic, LLM-driven analytical workflows** that can reason, compute, observe results, and optionally generate visualizations.

The system allows users to:

- ask natural-language business questions,
- have an LLM reason about intent and analytical strategy,
- retrieve and compute over structured business data,
- and validate results through observation loops.

This project is designed as a **research and learning platform** for agentic analytics — not a production BI tool.

---

## Project Status

⚠️ **Active Development**

The system is under active architectural evolution, focused on:

- improving reasoning reliability,
- reducing prompt and execution failure propagation,
- increasing debuggability of agent workflows,
- and supporting optional downstream visualization without destabilizing analysis.

Breaking changes may occur as the architecture evolves.

---

## Architecture: Binary-Responsibility Agent Graph

<div align="center">
  <img src="Binary-Responsibility Agent Graph.png" width="75%" />
</div>

<br>

The system is built around a **Binary-Responsibility Agent Graph**, guided by the following principles:

### 1. Binary Branching

Each node has **at most two outgoing paths**, ensuring that:
- decisions remain local,
- control flow is predictable,
- and failure modes are easier to trace.

### 2. Single Responsibility per Node

Each node performs **one clearly defined task**, such as:
- intent interpretation,
- context distillation,
- request classification,
- planning,
- execution,
- and observation.

This reduces prompt complexity and limits error propagation.

### 3. Explicit Planning–Execution–Observation Loops

Both analytical reasoning and visualization workflows follow a consistent loop:

- **Plan**: generate a structured, constrained plan  
- **Execution**: run code or actions in a controlled environment  
- **Observation**: validate semantic and functional correctness  

Failures trigger targeted correction loops rather than global retries.

### 4. Downstream Visualization as Optional

Infographic / visualization generation is treated as a **post-analysis concern**:
- analytical correctness is established first,
- visual output is generated only when relevant,
- visualization failures do not invalidate analytical results.

This separation improves system stability.

---

## High-Level System Structure

```sh
.
├── agent/              # LangGraph-based agent and node definitions
├── context/            # Runtime context objects shared across nodes
├── docker_script/      # Database initialization & synthetic data seeding
├── language_model/     # LLM abstraction layer
├── memory/             # Conversational and short-term memory persistence
├── util/               # Shared utilities
└── main.py             # Application entry point
```

## Features

- 🧠 **Agentic Reasoning Pipeline**

  Intent → classification → planning → execution → observation.

- 📊 **Business Analytics Focus**  

  Designed for descriptive and diagnostic analysis (with room to grow).

- 🧾 **Structured LLM Outputs**

  Enforced via Pydantic schemas.

- 🧩 **LangGraph-based Orchestration**

  Explicit state transitions and execution control.

- 🐳 **Fully Containerized Execution**
- 🗃️ **External PostgreSQL Integration**
- 🧪 **Synthetic Data Seeding for Development**

## Getting Started

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

### Installation

Clone the repository:

```sh
git clone https://github.com/reyharighy/cba-agentic-ai.git
cd cba-agentic-ai
```

---

### Running the System

Using docker:

```sh
docker compose up -d --build
```

Then open:

```sh
http://localhost:8501
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
