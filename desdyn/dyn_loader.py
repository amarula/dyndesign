from typing import Type


class DynLoader:
    """Toolset for dynamic loading."""

    @staticmethod
    def load_class(module_name: str, class_name: str = None) -> Type:
        """Dynamically load a class from a python module.

        :param module_name: name of the module to import.
        :param class_name: name of the class in the module to import.
        :return: imported class.
        """
        if not class_name: class_name = module_name
        loaded_module = __import__(module_name, fromlist=class_name)
        return getattr(loaded_module, class_name)
