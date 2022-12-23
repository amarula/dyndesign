"""Merge a base class with one or more extension classes."""

from functools import wraps
from typing import Any, Callable, Dict, List, Tuple, Type, Union
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


def __decorator_builder(
    func: Callable,
    decorator_instance: Callable,
    is_last_decorator: bool = False
) -> Callable:
    """Build a single decorator wrapper around a method using an instance of decorator.

    :param func: method to be decorated.
    :param decorator_instance: instance of decorator.
    :param is_last_decorator: whether the decorator is the last in the pipeline or not.
    :return: decorator wrapper.
    """
    args_from = 2 if is_last_decorator else 1
    @wraps(func)
    def dynamic_decorator_func(*args, **kwargs) -> Any:
        filtered_args, filtered_kwargs = __adapt_arguments(decorator_instance, func, *args[args_from:], **kwargs)
        return decorator_instance(args[0], *filtered_args, **filtered_kwargs)
    return dynamic_decorator_func


def __merged_decorator_builder(
    func: Callable,
    decorator_instances: List[Callable]
) -> Callable:
    """Build a merged decorator wrapper from two or more instances of decorator (called in pipeline).

    :param func: method to be decorated.
    :param decorator_instances: two or more instances of decorator.
    :return: merged decorator wrapper.
    """
    decorator_instance =  decorator_instances.pop()
    if decorator_instances:
        return __merged_decorator_builder(
            __decorator_builder(func, decorator_instance),
            decorator_instances=decorator_instances
        )
    else:
        return __decorator_builder(func, decorator_instance, is_last_decorator=True)


def __merge_not_overloaded(classes: List[Type], method: str) -> Union[Callable, None]:
    """Build a merged method by calling all the same-name method instances from the merged classes. If the method is
    used as a decorator (via `decoratewith`), then all the decorator instances are merged and called in pipeline.

    :param classes: merged classes.
    :param method: name of the method to be merged.
    :return: merged method if two or more method instances are found, None otherwise.
    """
    all_method_instances = [getattr(cur_class, method) for cur_class in classes if method in dir(cur_class)]
    if len(all_method_instances) < 2:
        return None

    def call_all_method_instances(obj, *args, **kwargs):
        method_instances = all_method_instances.copy()
        returned_value = None
        if __is_method_used_as_decorator(*args):
            decorated_method = __merged_decorator_builder(args[0], method_instances)
            returned_value = decorated_method(obj, *args, **kwargs)
        else:
            for method_instance in method_instances:
                if not inspect.ismethoddescriptor(method_instance):
                    filtered_args, filtered_kwargs = __adapt_arguments(method_instance, *args, **kwargs)
                    returned_value = method_instance(obj, *filtered_args, **filtered_kwargs)
        return returned_value

    return call_all_method_instances


def __preprocess_classes(all_classes: Any) -> List[Type]:
    """Dynamically import classes if passed as strings."""
    return [importclass(class_id) if type(class_id) == str else class_id for class_id in all_classes]


def mergeclasses(base_class: Any,
    *extension_classes: Any,
    invoke_all: List[str] = None # type: ignore
) -> Type:
    """Merge (i.e., extend) a base class with one or more extension classes. If more than one extension classes are
    provided, then the classes are extended in sequence following the order of `extension_classes`.

    :param base_class: base class.
    :param extension_classes: extension classes.
    :param invoke_all: list of methods (in addition to `__init__`) whose instances are invoked (if present) from all
                       the merged classes, rather than being overloaded by the instance from the rightmost class.
    :return: merged class.
    """
    all_classes = __preprocess_classes((base_class,) + extension_classes)
    invoke_all = ["__init__"] + (invoke_all or [])
    methods_not_oveloaded = {
        method: merged for method in invoke_all if (merged := __merge_not_overloaded(all_classes, method))
    }
    return type(
        all_classes[0].__name__,
        tuple(all_classes[::-1]),
        methods_not_oveloaded
    )
