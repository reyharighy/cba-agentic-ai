# standard
from collections.abc import Callable
from functools import wraps
from typing import (
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
        """
        Docstring for decorator

        :param func: Description
        :type func: Callable[P, R]
        :return: Description
        :rtype: Callable[P, R]
        """
        if cache_type == "data":
            cached_func = st.cache_data(show_spinner=spinner_text)(func)
        else:
            cached_func = st.cache_resource(show_spinner=spinner_text)(func)

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs):
            return cached_func(*args, **kwargs)

        return wrapper

    return decorator
