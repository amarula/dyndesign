"""Singletonmeta v. 1.0.05 """
from typing import Any


class SingletonMeta(type):
    """Meta class to instantiate singleton classes."""

    _instances: Any = {}

    def __call__(cls, *args, **kwargs) -> type:
        """Return the singleton class instance, if any instance is found, otherwise create and return a new singleton
        class instance.

        :return: singleton class instance.
        """
        if cls not in cls._instances:
            instance = super(SingletonMeta, cls).__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


    @classmethod
    def destroy(cls):
        """Delete all the instances of the singleton class."""
        cls._instances = {}
