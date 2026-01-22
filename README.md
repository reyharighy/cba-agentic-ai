<div id="top">

<div align="center">

# CONVERSATIONAL BUSINESS ANALYTICS

<em>Agentic AI for Interactive Business Analytics & Reasoning</em>

<em>Built with:</em>

<img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat&logo=Python&logoColor=white">
<img src="https://img.shields.io/badge/Streamlit-FF4B4B.svg?style=flat&logo=Streamlit&logoColor=white">
<img src="https://img.shields.io/badge/LangChain-1C3C3C.svg?style=flat&logo=LangChain&logoColor=white">
<img src="https://img.shields.io/badge/LangGraph-4B5563.svg?style=flat">

<img src="https://img.shields.io/badge/Docker-2496ED.svg?style=flat&logo=Docker&logoColor=white">
<img src="https://img.shields.io/badge/PostgreSQL-4169E1.svg?style=flat&logo=PostgreSQL&logoColor=white">
<img src="https://img.shields.io/badge/SQLAlchemy-D71F00.svg?style=flat&logo=SQLAlchemy&logoColor=white">

</div>

## Project Status (Development Branch)

⚠️ Active Architectural Experiment

This branch contains ongoing architectural changes to the agent graph, focused on improving reliability, debuggability, and extensibility of the system.

Primary focus:

- Downstream infographic / visualization pipeline
- Clear separation between analytical reasoning and visual output generation
- Simplified agent graph with constrained branching

This branch intentionally diverges from main and may introduce breaking changes.

## Binary-Responsibility Agent Graph

<div align="center"> <img src="Binary-Responsibility Agent Graph.png" width="75%" /> </div>

This branch introduces a revised agent graph design based on the following principles:
- **Binary branching**
  
  Each node has at most two outgoing paths, keeping decisions local and predictable.

- **Single responsibility per node**

  Nodes perform one well-defined task to reduce prompt complexity and failure propagation.

- **Explicit downstream visualization**

  Infographic generation is treated as an optional, post-analysis process rather than being embedded inside analytical reasoning.

- **Consistent planning–execution–observation loops**

  Applied across analysis and visualization phases for uniform control and recovery behavior.

The goal is not to add more steps, but to:

- simplify reasoning at each node
- improve debuggability and traceability
- enable downstream extensions (e.g. charts, infographics) without destabilizing core analysis

This design reflects practical constraints of LLM-based agents, where smaller, focused reasoning steps are more reliable than large, multi-purpose nodes.

⚠️ This design is under active iteration and may change rapidly.

## Relationship to main

- `main` represents the last stable architectural baseline
- This branch explores an alternative graph design
- If proven superior, this design may replace the current architecture in `main`

<div align="left"><a href="#top">⬆ Return</a></div>
