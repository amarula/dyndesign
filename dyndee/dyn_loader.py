from typing import Type


class DynLoader:
    """Toolset for class dynamic loading."""

    @staticmethod
    def import_class(module_name: str, class_name: str = '') -> Type:
        """Dynamically import a class from a python module.

        :param module_name: name of the module to import.
        :param class_name: name of the class in the module to import, if different from the module's name.
        :return: dynamically imported class.
        """
        if not class_name:
            module_name, class_name = module_name.rsplit('.', 1)
        loaded_module = __import__(module_name, fromlist=class_name)
        return getattr(loaded_module, class_name)
