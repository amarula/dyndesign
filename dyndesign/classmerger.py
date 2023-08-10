from functools import wraps
from typing import Any, Callable, List, Tuple, Type, Union

from dyndesign.dynloader import preprocess_classes
from dyndesign.utils.signature import adapt_arguments, call_method_with_adapted_args
from dyndesign.utils.inspector import is_func_in_stack

__all__ = ["mergeclasses"]

DECORATED_STACK_FUNCTION_NAME = 'dynamic_decorator_func'


def __is_method_used_as_decorator(*args) -> bool:
    """
    Detect whether a method is being used as a decorator via `decoratewith` or not.

    :param args: Input arguments.
    :return: True if the method is used as a decorator, False otherwise.
    """
    try:
        return callable(args[0]) and is_func_in_stack(DECORATED_STACK_FUNCTION_NAME)
    except IndexError:
        return False


def __decorator_builder(
        func: Callable,
        decorator_instance: Callable,
        is_last_decorator: bool = False
) -> Callable:
    """
    Build a single decorator wrapper around a method using an instance of a decorator.

    :param func: The method to be decorated.
    :param decorator_instance: The instance of the decorator.
    :param is_last_decorator: Whether the decorator is the last in the chain or not.
    :return: The decorator wrapper.
    """
    args_from = 2 if is_last_decorator else 1

    @wraps(func)
    def dynamic_decorator_func(*args, **kwargs) -> Any:
        filtered_args, filtered_kwargs = adapt_arguments(decorator_instance, func, *args[args_from:], **kwargs)
        return decorator_instance(args[0], *filtered_args, **filtered_kwargs)

    return dynamic_decorator_func


def __merged_decorator_builder(
        func: Callable,
        decorator_instances: List[Callable]
) -> Callable:
    """
    Build a merged decorator wrapper from two or more instances of decorators (called in chain).

    :param func: The method to be decorated.
    :param decorator_instances: Two or more instances of decorators.
    :return: The merged decorator wrapper.
    """
    decorator_instance = decorator_instances.pop()
    if decorator_instances:
        return __merged_decorator_builder(
            __decorator_builder(func, decorator_instance),
            decorator_instances=decorator_instances
        )
    else:
        return __decorator_builder(func, decorator_instance, is_last_decorator=True)


def __merge_not_overloaded(
        classes: Tuple[Type, ...],
        method: str,
        strict_merged_args: bool
) -> Union[Callable, None]:
    """
    Build a merged method by calling all instances of the same-name method from the merged classes. If the method is
    used as a decorator (via `decoratewith`), then all decorator instances are merged and called in a chain.

    :param classes: Merged classes.
    :param method: The name of the method to be merged.
    :param strict_merged_args: Whether a `TypeError` exception is raised or not in case one or more positional
                               arguments are missing.
    :return: The merged method if two or more method instances are found, None otherwise.
    """
    all_method_instances = [getattr(cur_class, method) for cur_class in classes if method in dir(cur_class)]
    if len(all_method_instances) < 2:
        return None

    def call_all_method_instances(obj: object, *args, **kwargs):
        method_instances = all_method_instances.copy()
        returned_value = None
        if __is_method_used_as_decorator(*args):
            decorated_method = __merged_decorator_builder(args[0], method_instances)
            returned_value = decorated_method(obj, *args, **kwargs)
        else:
            for method_instance in method_instances:
                returned_value = call_method_with_adapted_args(
                        method_instance,
                        obj,
                        *args,
                        strict_missing_args=strict_merged_args,
                        **kwargs
                )
        return returned_value

    return call_all_method_instances


@preprocess_classes
def mergeclasses(
        *all_classes: Type,
        invoke_all: Union[List[str], None] = None,
        strict_merged_args=True
) -> Type:
    """
    Merge a base class with one or more extension classes. If more than one extension class is provided, then the
    classes are merged in sequence following the order of `extension_classes`.

    :param all_classes: Base and extension classes.
    :param invoke_all: List of methods (in addition to `__init__`) whose instances are invoked (if present) from all
                       the merged classes, rather than being overloaded by the instance from the rightmost class.
    :param strict_merged_args: Controls whether a `TypeError` exception is raised or not in case one or more positional
                               arguments are missing in the `invoke_all` methods. If set to True (default value),
                               an exception is raised, otherwise methods with missing arguments are silently skipped.
    :return: Merged class.
    """
    invoke_all = ["__init__"] + (invoke_all or [])
    methods_not_overloaded = {
        method: merged for method in invoke_all if (
            merged := __merge_not_overloaded(all_classes, method, strict_merged_args)
        )
    }
    return type(
        all_classes[0].__name__,
        tuple(all_classes[::-1]),
        methods_not_overloaded
    )
