"""Create and destroy Singleton classes."""

from typing import Any

__all__ = ["SingletonMeta"]


class SingletonMeta(type):
    """Meta class to instantiate Singleton classes."""

    _instances: Any = {}

    def __new__(cls, name, bases, dct) -> type:
        """Add the class method `destroy_singleton` to the Singleton class."""
        def __destroy_singleton(_):
            cls.destroy(name)
        instance = super().__new__(cls, name, bases, dct)
        setattr(instance, 'destroy_singleton', __destroy_singleton)
        return instance


    def __call__(cls, *args, **kwargs) -> type:
        """Return the Singleton class instance, if any instance is found, otherwise create and return a new Singleton
        class instance.

        :return: Singleton class instance.
        """
        if cls not in cls._instances:
            instance = super(SingletonMeta, cls).__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


    @classmethod
    def destroy(cls, *class_names: str):
        """Delete all the instances of the Singleton classes whose names are passed as arguments. If no class name is
        passed, the instances of all the Singleton classes are deleted.

        :param class_names: names of the Singleton class instances to destroy.
        """
        if class_names:
            cls._instances = dict(filter(lambda k: k[0].__name__ not in class_names, cls._instances.items()))
        else:
            cls._instances = {}
