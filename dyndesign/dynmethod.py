"""Invoke methods that have been dynamically added to a class."""

from contextlib import AbstractContextManager
from functools import wraps
from operator import attrgetter
import re
from typing import Any, Callable, List

__all__ = ["decoratewith", "safeinvoke", "safezone"]


def __is_sub_object(method_name: str):
    return '.' in method_name


def __try_invoke_method(
    method_name: str,
    instance: object,
    *args,
    **kwargs
) -> Any:
    """Attempt to invoke a method of a class instance.

    :param method_name: name of a method of the class instance or path (in dot notation) to a method of a
                        sub-instance.
    :param instance: class instance that may optionally include the method referenced to with `method_name`.
    :return: value returned by the method, if such a method exists.
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
    method_sub_instance: str = None,  # type: ignore
    fallback: Callable = None  # type: ignore
) -> Callable:
    """Meta decorator to decorate a function with one or more decorator methods. Decorator methods can be, for
    example, class methods, methods dynamically added and/or methods of any sub-instance of a class instance.

    :param method_name_args: method name(s) of the one or more decorator methods.
    :param method_sub_instance: name of the sub-instance to be prepended to each method name.
    :return: method decorator.
    """
    method_names=list(method_name_args)
    if method_sub_instance:
        method_names = [f"{method_sub_instance}.{m}" for m in method_names]

    def dynamic_decorator_wrapper(
        func: Callable,
        method_names: List[str] = method_names
    ) -> Callable:
        """Decorator wrapper using one or more decorator methods in pipeline to decorate a function `func`.

        :param func: function to decorate.
        :param method_names: method name(s) of the one or more decorator methods.
        :return: decorated method.
        """
        method_name = method_names.pop()

        @wraps(func)
        def dynamic_decorator_func(instance, *args, **kwargs) -> Any:
            decorator_args = (func, ) + args
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
    fallback: Callable = None,  # type: ignore
    *args,
    **kwargs
) -> Any:
    """Attempt to invoke a method of a class instance. If the method is not found, code execution proceeds
    normally.

    :param method_name: name of a method of the class instance or path (in dot notation) to a method of a
                        sub-instance.
    :param instance: class instance that may optionally include the method referenced to with `method_name`.
    :return: value returned by the method, if such a method exists.
    """
    try:
        return __try_invoke_method(method_name, instance, *args, **kwargs)
    except ErrorMethodNotFound:
        if fallback:
            fallback(*args, **kwargs)
        return None


class safezone(AbstractContextManager):
    """Context manager to suppress `AttributeError` and `NameError` exceptions raised when specific methods are not
    available. After suppressing the exception, the execution proceeds with the next statement following the `with`
    statement.
    """

    def __init__(self,
        *method_names: str,
        fallback: Callable = None,  # type: ignore
    ):
        self.__method_names = method_names
        self.__fallback = fallback


    def __enter__(self):
        pass


    def __is_protected_name(self, excinst) -> bool:
        if not self.__method_names:
            return True
        try:
            method_name = excinst.name
        except AttributeError:
            method_name = re.findall(r"'([^']+)'", excinst.args[0])[-1]
        return method_name in self.__method_names


    def __exit__(self, exctype, excinst, exctb) -> bool:
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


class ErrorMethodNotFound(Exception):
    """Raised when a dynamic method cannot be found."""
