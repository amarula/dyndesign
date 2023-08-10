from contextlib import AbstractContextManager
from functools import wraps
from operator import attrgetter
import re
from typing import Any, Callable, List, Union

from dyndesign.exceptions import ErrorMethodNotFound

__all__ = ["decoratewith", "safeinvoke", "safezone"]


def __is_sub_object(method_name: str) -> bool:
    """
    Check if a method name represents a sub-object path.

    :param method_name: The method name to check.
    :return: True if the method name contains a dot, indicating a sub-object path, False otherwise.
    """
    return '.' in method_name


def __try_invoke_method(
        method_name: str,
        instance: object,
        *args,
        **kwargs
) -> Any:
    """
    Attempt to invoke a method of a class instance.

    :param method_name: Name of a method of the class instance or path (in dot notation) to a method of a
                        sub-instance.
    :param instance: Class instance that may optionally include the method referenced by `method_name`.
    :return: Value returned by the method, if such a method exists.
    """
    try:
        if __is_sub_object(method_name):
            method = attrgetter(method_name)(instance)
        else:
            method = getattr(instance, method_name)
    except AttributeError:
        raise ErrorMethodNotFound
    return method.__call__(*args, **kwargs)


def decoratewith(
        *method_name_args: str,
        method_sub_instance: Union[str, None] = None,
        fallback: Union[Callable, None] = None,
        disable_property: Union[str, None] = None
) -> Callable:
    """
    Meta decorator to decorate a function with one or more decorator methods. Decorator methods can be, for example,
    class methods, dynamically added methods, and/or methods of any sub-instance of a class instance.

    :param method_name_args: Method name(s) of one or more decorator methods.
    :param method_sub_instance: Name of the sub-instance to be prepended to each method name.
    :param fallback: Function to be invoked in case one or more methods in `method_name_args` are not found in
                     the instance object.
    :param disable_property: Name of a property to disable the decorator(s). If the property is found in the
                             instance object and is True, then the wrapped function is not decorated.
    :return: Method decorator.
    """
    method_names_global = list(method_name_args)
    if method_sub_instance:
        method_names_global = [f"{method_sub_instance}.{m}" for m in method_names_global]

    def dynamic_decorator_wrapper(
            func: Callable,
            method_names: List[str] = method_names_global
    ) -> Callable:
        """
        Decorator wrapper using one or more decorator methods in chain to decorate a function `func`.

        :param func: The function to decorate.
        :param method_names: Method name(s) of one or more decorator methods.
        :return: The decorated method.
        """
        method_name = method_names.pop()

        @wraps(func)
        def dynamic_decorator_func(instance, *args, **kwargs) -> Any:
            if disable_property and getattr(instance, disable_property, False):
                return func(instance, *args, **kwargs)
            decorator_args = (func,) + args
            if __is_sub_object(method_name):
                kwargs["decorated_self"] = instance
            try:
                return __try_invoke_method(method_name, instance, *decorator_args, **kwargs)
            except ErrorMethodNotFound:
                kwargs.pop("decorated_self", None)
                if fallback:
                    fallback(instance, *args, **kwargs)
                return func(instance, *args, **kwargs)

        if method_names:
            return dynamic_decorator_wrapper(dynamic_decorator_func, method_names=method_names)
        else:
            return dynamic_decorator_func

    return dynamic_decorator_wrapper


def safeinvoke(
        method_name: str,
        instance: object,
        *args,
        fallback: Union[Callable, None] = None,
        **kwargs
) -> Any:
    """
    Attempt to invoke a method of a class instance. If the method is not found, code execution proceeds normally.

    :param method_name: The method name of the class instance or path (in dot notation) to a method of a
                        sub-instance.
    :param instance: The class instance that may optionally include the method referenced by `method_name`.
    :param fallback: The function to be invoked in case the method `method_name` is not in `instance`.
    :return: The value returned by the method, if such a method exists.
    """
    try:
        return __try_invoke_method(method_name, instance, *args, **kwargs)
    except ErrorMethodNotFound:
        if fallback:
            fallback(*args, **kwargs)
        return None


class safezone(AbstractContextManager):
    """
    Context manager to suppress `AttributeError` and `NameError` exceptions raised when specific methods are not
    available. After suppressing the exception, execution proceeds with the next statement following the `with`
    statement.
    """

    def __init__(self, *method_names: str, fallback: Union[Callable, None] = None):
        self.__method_names = method_names
        self.__fallback = fallback

    def __enter__(self):
        pass

    def __is_protected_name(self, excinst) -> bool:
        """
        Check if an exception instance represents a protected method name.

        :param excinst: The exception instance to check.
        :return: True if the exception's method name is in the list of protected names, False otherwise.
        """
        if not self.__method_names:
            return True
        try:
            method_name = excinst.name
        except AttributeError:
            method_name = re.findall(r"'([^']+)'", excinst.args[0])[-1]
        return method_name in self.__method_names

    def __exit__(self, exctype, excinst, exctb) -> bool:
        """
        Handle the exit of the context manager.

        :param exctype: The exception type.
        :param excinst: The exception instance.
        :param exctb: The traceback.
        :return: True if the exception was handled and should be suppressed, False otherwise.
        """
        expected_exception = AttributeError if (
                'tb_frame' in dir(exctb) and
                'self' in exctb.tb_frame.f_locals
        ) else NameError
        result = (
                exctype is not None and
                issubclass(exctype, expected_exception) and
                self.__is_protected_name(excinst)
        )
        if result and self.__fallback:
            self.__fallback()
        return result
