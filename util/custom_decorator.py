"""
Docstring for util.custom_decorator
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
    Docstring for st_cache
    
    :param spinner_text: Description
    :type spinner_text: str
    :param cache_type: Description
    :type cache_type: Literal["data", "resource"]
    :return: Description
    :rtype: Callable[[Callable[P, R]], Callable[P, R]]
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
    Docstring for st_status_container
    
    :param processing_text_status: Description
    :type processing_text_status: str
    :param expanded: Description
    :type expanded: bool
    :return: Description
    :rtype: Callable[[Callable[P, R]], Callable[P, R]]
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
