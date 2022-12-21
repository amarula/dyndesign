"""Merge a base class with one or more extension classes."""

from typing import Any, Callable, Dict, List, Tuple, Type
from collections import deque
import inspect

from dyndesign.dynloader import importclass

__all__ = ["mergeclasses"]


DECORATED_STACK_FUNCTION_NAME = 'dynamic_decorator_func'


def __adapt_arguments(func: Callable, *args, **kwargs) -> Tuple[List, Dict]:
    """Filter `args` and `kwargs` based and the arguments accepted by an input function.

    :param func: input function.
    :param args: input arguments.
    :param kwargs: input keyword arguments.
    :return: filtered arguments and keyword arguments.
    """
    init_specs = inspect.getfullargspec(func)
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


def __is_method_used_as_decorator(*args) -> bool:
    """Detect whether a method is used as a decorator via `decoratewith` or not.

    :param args: input arguments.
    :return: True if the method is used as a decorator, False otherwise.
    """
    try:
        return (
            callable(args[0]) and
            next((True for s in inspect.stack() if s.function == DECORATED_STACK_FUNCTION_NAME), False)
        )
    except IndexError:
        return False


def __merge_not_overloaded(classes: List[Type], method: str) -> Callable:
    """Build a merged method by calling all the same-name method instances from the merged classes. If the method is
    used as a decorator (via `decoratewith`), then the wrapped function is invoked only by the first instance of the
    decorator. The following instances are passed a dummy lambda function as wrapped function, where the lambda returns
    the same value returned by the first instance.

    :param classes: merged classes.
    :param method: name of the method to be merged.
    :return: merged method.
    """
    method_instances = [getattr(cur_class, method) for cur_class in classes if method in dir(cur_class)]

    def call_all_method_instances(obj, *args, **kwargs):
        decorator_executed_once = False
        method_used_as_decorator = __is_method_used_as_decorator(*args)
        returned_value = None
        for method_instance in method_instances:
            if not inspect.ismethoddescriptor(method_instance):
                filtered_args, filtered_kwargs = __adapt_arguments(method_instance, *args, **kwargs)
                if decorator_executed_once:
                    filtered_args = (lambda *_: returned_value, *filtered_args[1:])
                returned_value = method_instance(obj, *filtered_args, **filtered_kwargs)
                if method_used_as_decorator:
                    decorator_executed_once = True
        return returned_value

    return call_all_method_instances


def __preprocess_classes(all_classes: Any) -> List[Type]:
    """Dynamically import classes if passed as strings."""
    return [importclass(class_id) if type(class_id) == str else class_id for class_id in all_classes]


def mergeclasses(base_class: Any,
    *extension_classes: Any,
    exclude_overload: List[str] = None # type: ignore
) -> Type:
    """Merge (i.e., extend) a base class with one or more extension classes. If more than one extension classes are
    provided, then the classes are extended in sequence (from the first one to the last).

    :param base_class: base class.
    :param extension_classes: extension classes.
    :param exclude_overload: list of methods (in addition to `__init__`) whose instances from all the merged classes
                             (if present) are invoked, rather than being overloaded by the instance from the rightmost
                             class.
    :return: merged class.
    """
    all_classes = __preprocess_classes((base_class,) + extension_classes)
    exclude_overload = ["__init__"] + (exclude_overload or [])
    methods_not_oveloaded = {method: __merge_not_overloaded(all_classes, method) for method in exclude_overload}
    return type(
        all_classes[0].__name__,
        tuple(all_classes[::-1]),
        methods_not_oveloaded
    )
