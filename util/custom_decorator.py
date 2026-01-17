"""
Custom decorators for application-level concerns.

This module defines lightweight decorators that standardize
cross-cutting behaviors.
"""
# standard
from functools import wraps
from typing import (
    Callable,
    Literal,
    ParamSpec,
    TypeVar,
)

# third-party
import streamlit as st

P = ParamSpec("P")
R = TypeVar("R")

def st_cache(spinner_text: str, cache_type: Literal["data", "resource"]) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator factory for unified caching behavior.

    This decorator provides a consistent interface for applying
    caching semantics while abstracting away the underlying
    caching mechanism.
    """
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        if cache_type == "data":
            cached_func = st.cache_data(show_spinner=spinner_text)(func)
        else:
            cached_func = st.cache_resource(show_spinner=spinner_text)(func)

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs):
            return cached_func(*args, **kwargs)

        return wrapper

    return decorator

def st_status_container(processing_text_status: str, expanded: bool = False) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator factory for execution status visualization.

    This decorator wraps a function execution within a
    transient status container, intended to communicate
    processing state during interactive workflows.
    """
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            with st.status(processing_text_status, expanded=expanded) as status:
                result = func(*args, **kwargs)
                status.update(state="complete")

            return result

        return wrapper

    return decorator
