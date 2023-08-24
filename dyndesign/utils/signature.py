from typing import Any, Callable, Dict, List, Optional, Tuple
from collections import deque
import re
import inspect

from dyndesign.utils.inspector import get_arguments


def __is_missing_arguments_exception(exception: Exception, instance: Callable) -> bool:
    """
    Detect whether an exception is triggered by missing positional arguments during method invocation.

    :param exception: The exception to check.
    :param instance: The method invoked or class instantiated.
    :return: True if the exception is due to missing positional arguments, False otherwise.
    """
    exception_message = exception.args[0]
    name, qualname = (
        ('__init__', f"{instance.__name__}.__init__") if isinstance(instance, type)
        else (instance.__name__, instance.__qualname__)
    )
    matching_regex = fr'({re.escape(name)}|{re.escape(qualname)})\(\) missing'
    return bool(re.match(matching_regex, exception_message))


def adapt_arguments(func: Callable, *args, **kwargs) -> Tuple[List, Dict]:
    """
    Filter 'args' and 'kwargs' based on the arguments accepted by a given function.

    :param func: The input function.
    :param args: The input arguments.
    :param kwargs: The input keyword arguments.
    :return: Filtered arguments and keyword arguments.
    """
    init_specs = get_arguments(func)
    if init_specs.varargs:
        res_args = list(args)
    else:
        func_args = init_specs.args[1:]
        arg_deque = deque(args)
        res_args = []
        for func_arg in func_args:
            if func_arg in kwargs:
                res_args.append(kwargs[func_arg])
                del kwargs[func_arg]
            elif arg_deque:
                res_args.append(arg_deque.popleft())

    func_kwargs = init_specs.kwonlydefaults or {}
    if init_specs.varkw:
        res_kwargs = kwargs
    else:
        res_kwargs = {key: value for key, value in kwargs.items() if key in func_kwargs}

    return res_args, res_kwargs


def call_obj_with_adapted_args(instance: Callable, obj: Optional[object], *args, strict_missing_args: bool = True,
                               **kwargs) -> Any:
    """
    Call the given instance with adapted arguments.

    :param instance: The callable instance (function or method).
    :param obj: The object on which the method will be called.
    :param args: The arguments to pass.
    :param strict_missing_args: If True, raises exceptions for missing arguments.
    :param kwargs: The keyword arguments to pass.
    :return: The result of the method call.
    """
    filtered_args, filtered_kwargs = adapt_arguments(instance, *args, **kwargs)
    try:
        if obj:
            filtered_args.insert(0, obj)
        return instance(*filtered_args, **filtered_kwargs)
    except TypeError as e:
        if strict_missing_args or not __is_missing_arguments_exception(e, instance):
            raise e


def call_method_with_adapted_args(instance: Callable, obj: Optional[object], *args, strict_missing_args: bool = True,
                                  **kwargs) -> Any:
    """
    Call the given instance method with adapted arguments.

    :param instance: The callable instance method.
    :param obj: The object on which the method will be called.
    :param args: The arguments to pass.
    :param strict_missing_args: If True, raises exceptions for missing arguments.
    :param kwargs: The keyword arguments to pass.
    :return: The result of the method call.
    """
    returned_value = None
    if not inspect.ismethoddescriptor(instance):
        returned_value = call_obj_with_adapted_args(
            instance,
            obj,
            *args,
            strict_missing_args=strict_missing_args,
            **kwargs
        )
    return returned_value
