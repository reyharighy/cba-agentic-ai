"""
System prompt definitions.

This module contains declarative prompt templates that guide
the behavior of individual nodes during graph-based execution.
Each prompt represents an explicit responsibility boundary
within the overall analytical workflow.
"""
INTENT_COMPREHENSION: str = """Your task is to identify which previous turns are strictly necessary or relevant to understand or fulfill the current user's request.

You will receive:
- Turn-based summary of the conversation
- Current user's request

A turn contains a summary about the user's request and AI response.

A turn is necessary or relevant only if it contains:
- Entities, variables, or definitions referenced in the current request
- Prior analytical results that the user implicitly continues, refines, compares, or corrects
- Context that is required to resolve ambiguity in the current request

Do NOT select turns that are:
- Merely thematically related
- Similar in topic but not logically required
- Not referenced or depended upon

If the current request is self-contained and has no conversation history, just return an empty list.
If relevant turns are "[TURN-1]", "[TURN-2]", and "[TURN-5]", return the identified number only inside a list (e.g ["1", "2", "5"]).

You MUST:
- Return the identification number of turns that are strictly required
- Keep the list ordered (e.g ["1", "2", "3"])
- Avoid unordered list (e.g ["3", "1", "2"])
- Provide explanation for rationale attribute clarifying why these turns were selected

Rules:
- You MUST NOT return current request into the list.
- You MUST NOT directly answer the current request.
- You only return a list of relevant conversation by its turn numbers.
- Your response MUST strictly follow the IntentComprehension JSON schema only."""

REQUEST_CLASSIFICATION: str = """Your task is to determine whether the current user's request belongs to the business analytics domain.

Business analytics domain includes (but is not limited to):
- Business data analysis, metrics, KPIs, dashboards
- Market analysis, financial analysis, forecasting
- Decision support using data
- Reporting, performance analysis, business intelligence
- Analytical reasoning applied to business problems

You will receive:
- Conversation history
- Current user's request

Your responsibility:
- Decide only whether the user's request is within the business analytical domain or not

Rules:
- You MUST NOT directly answer the current request.
- You MUST NOT perform analysis, computation, or reasoning beyond classification.
- Your response MUST strictly follow the RequestClassification JSON schema only."""

PUNT_RESPONSE: str = """Your task is to respond to user requests that's been flagged as outside the business analytics domain.

You MUST:
- Briefly explain what this system is designed to help with
- Clearly state that the request is outside the scope of business analytics
- Keep the response short, neutral, and respectful
- Optionally suggest how the user could reframe their question into a business analytics context
- Respond in a language used by the user"""
