from enum import IntEnum, auto
import inspect
import re
from types import FrameType
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


def get_class_name(frame: FrameType) -> Optional[str]:
    """
    Retrieve the class name from the frame, if the frame is in a class context, None otherwise.

    :param frame: The frame to retrieve the class name from.
    :return: The retrieved class name.
    """
    return frame.f_locals['__qualname__']


def get_instance_class_name(frame: FrameType) -> Optional[str]:
    """
    Retrieve the instance class name from the frame, if the frame is in an instance context, None otherwise.

    :param frame: The frame to retrieve the instance class name from.
    :return: The retrieved instance class name.
    """
    return frame.f_locals['self'].__class__.__name__


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


def is_method_not_defined_in_class(method: Any) -> bool:
    """
    Check if a method is a method descriptor, i.e. the passed method is not defined within the class code.

    :param method: The method to be checked.
    :return: True if the method is not defined within the class code, False otherwise.
    """
    return inspect.ismethoddescriptor(method)


def is_invoking_method_in_one_line(haystack_method: Callable, needle_method_name: str) -> bool:
    """
    Check if a haystack method has a call to a needle method within its source code.

    :param haystack_method: The method whose code is to be searched for.
    :param needle_method_name: The name of the method call to search for.
    :return: True if the call to the needle method is found in the haystack method's code, False otherwise.
    """
    try:
        method_code = inspect.getsource(haystack_method)
        return bool(re.search(fr"\n\s*{re.escape(needle_method_name)}\(.*?\)\n", method_code))
    except TypeError:
        return False
