<div id="top">

<div align="center">

# CONVERSATIONAL BUSINESS ANALYTICS (Agentic)

<em>Agentic AI for Interactive Business Analytics & Reasoning</em>

<em>Built with:</em>

<img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat&logo=Python&logoColor=white">
<img src="https://img.shields.io/badge/Streamlit-FF4B4B.svg?style=flat&logo=Streamlit&logoColor=white">
<img src="https://img.shields.io/badge/LangChain-1C3C3C.svg?style=flat&logo=LangChain&logoColor=white">
<img src="https://img.shields.io/badge/LangGraph-4B5563.svg?style=flat">
<img src="https://img.shields.io/badge/Pydantic-E92063.svg?style=flat&logo=Pydantic&logoColor=white">
<br>
<img src="https://img.shields.io/badge/Docker-2496ED.svg?style=flat&logo=Docker&logoColor=white">
<img src="https://img.shields.io/badge/PostgreSQL-4169E1.svg?style=flat&logo=PostgreSQL&logoColor=white">
<img src="https://img.shields.io/badge/SQLAlchemy-D71F00.svg?style=flat&logo=SQLAlchemy&logoColor=white">
<img src="https://img.shields.io/badge/Ruff-D7FF64.svg?style=flat&logo=Ruff&logoColor=black">

</div>

## Table of Contents

- [Overview](#overview)
- [Design Philosophy](#design-philosophy)
- [Architecture](#architecture)
- [Features](#features)
- [Project Status](#project-status)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Environment Setup](#environment-setup)
  - [Installation](#installation)
  - [Running the System](#running-the-system)
- [Synthetic Data & External Database](#synthetic-data--external-database)
- [Notes for Contributors](#notes-for-contributors)

## Overview

**Conversational Business Analytics (CBA – Agentic)** is an experimental, open-source system for building **agentic, LLM-driven business analytics workflows**.

The system allows users to:

- ask natural-language business questions,
- have an LLM reason about intent and analytical strategy,
- execute data analysis through a controlled runtime,
- and present results interactively via a Streamlit UI.

This project is designed as a **learning, research, and prototyping platform**, not a finished BI product.

## Design Philosophy

This project follows a few non-negotiable principles:

- **Explicit contracts over implicit behavior**: LLM outputs are constrained using Pydantic schemas.
- **Graph-based reasoning**: Analytical workflows are modeled explicitly using LangGraph.
- **Reproducible environments**: Docker is the default execution path.
- **Synthetic data first**: External business data is generated for development and testing.
- **Separation of concerns**: UI, orchestration, schemas, runtime, and persistence are isolated.

## Architecture

High-level structure:

```sh
.
├── application/ # Streamlit UI & user interaction
├── cache/ # Cold start & caching utilities
├── context/ # Internal datasets & contextual memory
├── docker_scripts/ # External DB seeding & synthetic data factory
├── graph/ # LangGraph nodes, runtime, orchestration
├── schema/ # Pydantic schemas for LLM structured outputs
├── schema/ # Custom Streamlit decorator
└── main.py # Application entrypoint
```

Key ideas:

- **`schema/`** defines strict contracts for LLM outputs.
- **`graph/`** encodes reasoning and execution as a stateful graph.
- **`docker_scripts/`** exists solely to provision external business data.

## Features

- 🧠 **Agentic Reasoning Pipeline**

  Intent → classification → planning → execution → observation.

- 📊 **Business Analytics Focus**  

  Designed for descriptive and diagnostic analysis (with room to grow).

- 🧾 **Structured LLM Outputs**

  Enforced via Pydantic schemas.

- 🧩 **LangGraph-based Orchestration**

  Explicit state transitions and execution control.

- 🌐 **Interactive Streamlit UI**
- 🐳 **Fully Containerized Execution**
- 🗃️ **External PostgreSQL Integration**
- 🧪 **Synthetic Data Seeding for Development**

## Project Status

⚠️ **Work in Progress**

Current focus:

- Core reasoning pipeline stability
- Schema design and validation
- Runtime observability
- Developer ergonomics

Not production-ready. APIs, structure, and assumptions may change.

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

- Synthetic data is stored in docker_scripts/synthetic_data.csv
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

<div align="left"><a href="#top">⬆ Return</a></div>
