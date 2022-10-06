from operator import attrgetter
from typing import Any, Callable, List


class DynamicDecorator:
    """Use methods added dynamically as decorators."""

    @staticmethod
    def __decorate_with_method_in_instance(
        method_name: str,
        instance: object,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Decorate function `func` with method `method_name` if `method_name` is in the namespace of `instance`,
        otherwise call `func`.

        :param method_name: method name of the method to use as decorator.
        :param instance: class instance that may optionally include method `method_name`.
        :param func: function to decorate.
        :return: return value of `func`, if any.
        """
        if hasattr(instance, method_name):
            return getattr(instance, method_name).__call__(func, *args, **kwargs)
        else:
            return func(instance, *args, **kwargs)


    @staticmethod
    def __decorate_with_method_in_sub_instance(
        method_name: str,
        instance: object,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Decorate function `func` with method `method_name`, wherein `method_name` is the path to a method in the
        namespace of a sub-instance of `instance`. If such a method is not found, then call `func`.

        :param method_name: path (in dot notation) to a method to use as decorator.
        :param instance: class instance that may optionally include the method referenced with the path `method_name`.
        :param func: function to decorate.
        :return: return value of `func`, if any.
        """
        try:
            method = attrgetter(method_name)(instance)
        except AttributeError:
            return func(instance, *args, **kwargs)
        return method.__call__(func, instance, *args, **kwargs)


    @classmethod
    def decorate_with(cls,
        *method_name_args: str,
        method_sub_instance: str = None
    ) -> Callable:
        """Meta decorator to decorate a function with one or more decorator methods. Decorator methods can be, for
        example, class methods, methods dynamically created and/or methods of any sub-instance of a class instance.

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
                if '.' in method_name:
                    return cls.__decorate_with_method_in_sub_instance(method_name, instance, func, *args, **kwargs)
                else:
                    return cls.__decorate_with_method_in_instance(method_name, instance, func, *args, **kwargs)

            if method_names:
                return dynamic_decorator_wrapper(dynamic_decorator_func, method_names=method_names)
            else:
                return dynamic_decorator_func

        return dynamic_decorator_wrapper
