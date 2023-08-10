from enum import IntEnum, auto
import inspect
import re
from typing import Any, Callable, Optional


class BackLevels(IntEnum):
    """Possible back levels for `back_frame`"""
    BACK_LEVEL_1 = auto()
    DEFAULT_BACK_LEVEL = auto()
    BACK_LEVEL_3 = auto()
    BACK_LEVEL_4 = auto()
    BACK_LEVEL_5 = auto()


def back_frame(back_level: Optional[int] = None) -> Any:
    """
    Retrieve the frame that is 'back_level' frames back from the current frame.

    :param back_level: The number of frames to go back in the call stack (default is 2).
    :return: The retrieved frame.
    """
    current_frame = inspect.currentframe()
    for _ in range(back_level or BackLevels.DEFAULT_BACK_LEVEL):
        current_frame = current_frame.f_back  # type: ignore
    return current_frame


def is_func_in_stack(func_name: str) -> bool:
    """
    Check if a function named 'func_name' exists in the call stack.

    :param func_name: The name of the function to search for.
    :return: True if the function is found in the call stack, False otherwise.
    """
    return any(s.function == func_name for s in inspect.stack())


def get_arguments(func: Callable) -> inspect.FullArgSpec:
    """
    Retrieve the arguments and associated information for a given function.

    :param func: The function to inspect.
    :return: An instance of inspect.FullArgSpec containing argument details.
    """
    return inspect.getfullargspec(func)
