"""Create and destroy Singleton classes."""

from typing import Any


class SingletonMeta(type):
    """Meta class to instantiate Singleton classes."""

    _instances: Any = {}

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
    def destroy(cls):
        """Delete all the instances of the Singleton class."""
        cls._instances = {}
