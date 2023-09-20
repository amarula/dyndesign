from types import SimpleNamespace
from typing import Any, Type

from .exposed_class_config import ClassConfig
import dyndesign.exceptions as exc


class DependencyConfiguration:
    """
    The class embodying a class dependency configuration, whose instances directly corresponds to the ClassConfig
    objects passed to the `@dynconfig` decorator in a one-to-one fashion.
    """

    def __init__(self, class_config: ClassConfig):
        """
        Initialize a class dependency configuration.

        :param class_config: the user-defined class configuration used to initialize the class dependency configuration.
        """
        self.validate_class_config(class_config)
        self.__attributes = class_config.__dict__
        self.selected_option = None
        self.must_be_added = False

    def __getattr__(self, name: str) -> Any:
        """
        Get a configuration attribute by name.

        :param name: The name of the attribute to return.
        :return: The attribute corresponding to the name.
        """
        return self.__attributes.get(name)

    def append(self, _):
        """
        Raise an `AttributeError` exception if `append` is called in a DependencyConfiguration instance.
        """
        raise AttributeError

    def setup(self, selected_option: Any, force_add: bool):
        """
        Set up the configuration for a Class Dependency.

        :param selected_option: The value of the Building Option associated with this dependency.
        :param force_add: Whether this dependency must be added or not regardless of the Building Options passed.
        """
        self.selected_option = selected_option
        self.must_be_added = bool(selected_option) or force_add

    def set_default_class_config(self, defaults: SimpleNamespace):
        """
        Set default values in a dependency configuration if the corresponding keys do not exist.

        :param defaults: The default values.
        """
        self.__attributes.update((k, v) for k, v in defaults.__dict__.items() if self.__attributes.get(k) is None)

    @staticmethod
    def validate_class_config(class_config: ClassConfig):
        """
        Validate the user-defined class configuration.

        :param class_config: The configuration to be validated.
        """
        if not class_config.inherit_from and not class_config.component_class:
            raise exc.ClassConfigMissingDependency(
                "ClassConfig configurator must include either one of the following fields: 'inherit_from' and "
                "'component_class'"
            )
        if class_config.inherit_from and class_config.component_class:
            raise exc.ClassConfigDependencyOverflow(
                "ClassConfig configurator must include only one of the following fields: 'inherit_from' and "
                "'component_class'"
            )

    def validate_component_configuration(self, base_class: Type):
        """
        Validate the class component configuration.

        :param base_class: The base class upon which to build the new class.
        """
        if not self.component_attr:
            raise exc.ClassConfigMissingComponentAttr(
                "ClassConfig configurator must include the 'component_attr' field if the 'component_class' field is "
                "present"
            )
        if not hasattr(base_class, str(self.injection_method)):
            raise exc.ClassConfigMissingComponentInjectionMethod(
                "The method specified in the 'injection_method' field does not exist in the base class"
            )
