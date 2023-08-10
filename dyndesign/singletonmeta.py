from typing import Any

__all__ = ["SingletonMeta"]


class SingletonMeta(type):
    """A metaclass to manage Singleton classes."""

    _instances: Any = {}

    def __new__(cls, name, bases, dct) -> type:
        """Create the Singleton class and add the class method `destroy_singleton` to it."""
        def __destroy_singleton(_):
            cls.destroy(name)

        instance = super().__new__(cls, name, bases, dct)
        setattr(instance, 'destroy_singleton', __destroy_singleton)
        return instance

    def __call__(cls, *args, **kwargs) -> type:
        """
        Return the Singleton class instance, creating a new instance if one does not already exist.

        :param args: Arguments to pass to the class constructor.
        :param kwargs: Keyword arguments to pass to the class constructor.
        :return: Singleton class instance.
        """
        if cls not in cls._instances:
            instance = super(SingletonMeta, cls).__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

    @classmethod
    def destroy(cls, *class_names: str):
        """
        Delete instances of Singleton classes based on provided class names.

        :param class_names: Names of the Singleton class instances to destroy.
                           If no class name is provided, instances of all Singleton classes are deleted.
        """
        if class_names:
            cls._instances = {k: v for k, v in cls._instances.items() if k.__name__ not in class_names}
        else:
            cls._instances = {}
