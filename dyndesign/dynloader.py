"""Import dynamically a class."""

from typing import Any, Callable, Type, Union

__all__ = ["importclass"]


def importclass(
    module_name: str,
    class_name: Union[str, None] = None
) -> Type:
    """Dynamically import a class from a python module.

    :param module_name: name of the module to import.
    :param class_name: name of the class in the module to import, if different from the module's name.
    :return: dynamically imported class.
    """
    if not class_name:
        module_name, class_name = module_name.rsplit('.', 1)
    loaded_module = __import__(module_name, fromlist=class_name)
    return getattr(loaded_module, class_name)


def preprocess_classes(func: Callable) -> Callable:
    """Decorator to convert dot-notated paths into string from positional arguments."""
    def __preprocess_classes_wrapper(*all_classes: Any, **kwargs: Any) -> Any:
        """Dynamically import classes if passed as strings."""
        classes_processed = (
            importclass(class_id) if type(class_id) == str else class_id
            for class_id in all_classes
        )
        return func(*classes_processed, **kwargs)
    return __preprocess_classes_wrapper
