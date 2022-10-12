"""DynMethods v. 1.0.05 """

from operator import attrgetter
from typing import Any, Callable, List


class ErrorMethodNotFound(Exception):
    """Raised when a dynamic method cannot be found."""


class DynMethods:
    """Invoke methods dynamically added to a class."""

    @staticmethod
    def __is_sub_object(method_name: str):
        return '.' in method_name


    @classmethod
    def __try_invoke_method(cls,
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
            if cls.__is_sub_object(method_name):
                method = attrgetter(method_name)(instance) 
            else:
                method = getattr(instance, method_name)
        except AttributeError:
            raise ErrorMethodNotFound
        return method.__call__(*args, **kwargs)


    @classmethod
    def decorate_with(cls,
        *method_name_args: str,
        method_sub_instance: str = ''
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

            def dynamic_decorator_func(instance, *args, **kwargs) -> Any:
                decorator_args = (func, ) + args
                if cls.__is_sub_object(method_name):
                    kwargs["decorated_self"] = instance
                try:
                    return cls.__try_invoke_method(method_name, instance, *decorator_args, **kwargs)
                except ErrorMethodNotFound:
                    kwargs.pop("decorated_self", None)
                    return func(instance, *args, **kwargs)

            if method_names:
                return dynamic_decorator_wrapper(dynamic_decorator_func, method_names=method_names)
            else:
                return dynamic_decorator_func

        return dynamic_decorator_wrapper


    @classmethod
    def invoke(cls,
        method_name: str,
        instance: object,
        *args,
        **kwargs
    ) -> Any:
        """Attempt to invoke a method of a class instance. If the method is not found code execution proceeds normally.

        :param method_name: name of a method of the class instance or path (in dot notation) to a method of a
                            sub-instance.
        :param instance: class instance that may optionally include the method referenced to with `method_name`.
        :return: value returned by the method, if such a method exists.
        """
        try:
            return cls.__try_invoke_method(method_name, instance, *args, **kwargs)
        except ErrorMethodNotFound:
            return None
