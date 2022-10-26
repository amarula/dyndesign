"""Merge a base class with one or more extension classes."""

from typing import Any, Callable, Dict, List, Tuple, Type
from collections import deque
import inspect

from dyndesign.dynloader import importclass


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


def __merge_class_inits(classes: List[Type]) -> Callable:
    """Build a merged constructor by calling the constructors of the merged classes.

    :param classes: merged classes.
    :return: merged constructor.
    """
    class_constructors = []
    for cur_class in classes:
        if '__init__' in dir(cur_class):
            class_constructors.append(cur_class.__init__)

    def init_all_classes(obj, *args, **kwargs):
        for class_constructor in class_constructors:
            if not inspect.ismethoddescriptor(class_constructor):
                filtered_args, filtered_kwargs = __adapt_arguments(class_constructor, *args, **kwargs)
                class_constructor(obj, *filtered_args, **filtered_kwargs)

    return init_all_classes


def __preprocess_classes(all_classes: Any) -> List[Type]:
    """Dynamically import classes if passed as strings."""
    result_classes = []
    for class_id in all_classes:
        if type(class_id) == str:
            cl = importclass(class_id)
        else:
            cl = class_id
        result_classes.append(cl)
    return result_classes


def mergeclasses(base_class: Any, *extension_classes: Any) -> Type:
    """Merge (i.e., extend) a base class with one or more extension classes. If more than one adapter classes are
    provided, then the classes are extended in sequence (from the first one to the last).

    :param base_class: base class.
    :param extension_classes: extension classes.
    :return: merged class.
    """
    all_classes = __preprocess_classes((base_class,) + extension_classes)
    init_all_classes = __merge_class_inits(all_classes)
    return type(
        all_classes[0].__name__,
        tuple(all_classes[::-1]),
        {"__init__": init_all_classes}
    )
