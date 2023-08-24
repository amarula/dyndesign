from typing import Callable, Dict, List, Type, Union

from .class_builder_config import ClassConfig
from .class_configuration_manager import ClassConfigurationManager
from .class_importer import TypeClassOrPath
from .class_storage import ClassStorage
from .parent_class_builder import ParentClassBuilder
from .component_class_builder import ComponentClassBuilder
from dyndesign.utils.inspector import get_arguments
from dyndesign.utils.misc import tuplefy
from dyndesign.exceptions import ClassConfigMissingDependency


class ClassBuilder:
    """
    Class Builder utilized to create a built class by applying the options selected from a class configuration settings
    to a base class.
    """

    def __init__(self, base_class: Type, config_manager: ClassConfigurationManager):
        """
        Initialize a ClassBuilder instance.

        :param base_class: The base class to be configured.
        :param config_manager: An instance of ClassConfigurationManager for loading class configuration.
        """
        self.__base_class = base_class
        self.__config_manager = config_manager

    def __is_option_selected(self, selector: Union[Callable, str]) -> bool:
        """
        Check if a configuration selector is enabled through the class options.

        :param selector: The configuration selector to check.
        :return: True if the selector is enabled, False otherwise.
        """
        if isinstance(selector, (staticmethod, classmethod)):
            selector = selector.__func__
        if callable(selector):
            args = get_arguments(selector).args
            values = (self.__CLASS_OPTIONS.get(arg, getattr(self.__base_class, arg, None)) for arg in args)
            return selector(*values)
        else:
            return bool(self.__CLASS_OPTIONS.get(selector))

    def __configure_dependent_class(self, dependent_class: TypeClassOrPath) -> Type:
        """
        Recursively configure a dependent class based on the class options.

        :param dependent_class: The dependent class or path to dependent class to be configured.
        :return: The built class.
        """
        dependent_class = self.__config_manager.class_importer.get_imported_class(dependent_class)
        if (not self.__config_manager.global_conf.build_recursively
                or dependent_class == self.__base_class
                or ClassStorage.is_already_built(dependent_class)):
            return dependent_class
        return ClassStorage.config_map[dependent_class].configure_class(self.__CLASS_OPTIONS)

    def __setup_class_configuration(self, options: Dict):
        """
        Set up the configuration for building a class.

        :param options: The configuration options.
        """
        self.__CLASS_OPTIONS = options
        self.__parent_class_builder = ParentClassBuilder(self.__base_class, self.__configure_dependent_class)
        self.__component_class_builder = ComponentClassBuilder(
            self.__base_class,
            self.__config_manager,
            self.__configure_dependent_class
        )

    def __prepare_class_dependency(self, option_selector: List[str], is_option_selected: bool,
                                   dependent_class_config: ClassConfig):
        """
        Prepare a dependent classes to be added to the base class based on the class configuration and whether the
        corresponding configuration option is selected or not.

        :param option_selector: The option selector corresponding to the component to be potentially added.
        :param is_option_selected: Whether the configuration option is selected or not.
        :param dependent_class_config: The class configuration of the dependent class to be added.
        """
        default_class = self.__config_manager.get_default_class(dependent_class_config)
        if is_option_selected or default_class:
            if dependent_class_config.inherit_from:
                parent_class = dependent_class_config.inherit_from if is_option_selected else default_class
                self.__parent_class_builder.add_parent_classes(parent_class)
            elif dependent_class_config.component_class:
                dependent_class_config.is_option_selected = is_option_selected
                self.__component_class_builder.select_component_class(option_selector, dependent_class_config)
            else:
                # This is a fallback in case the `ClassConfigMissingDependency` exception is not raised when validating
                # the `ClassConfig` object.
                raise ClassConfigMissingDependency

    def __prepare_class_dependencies(self):
        """
        Prepare the dependent classes to be added to the base class based on the selected options.
        """
        for option_selector in self.__config_manager.option_selectors:
            is_option_selected = self.__is_option_selected(option_selector)
            for dependent_class_config in tuplefy(self.__config_manager.class_conf[option_selector]):
                self.__prepare_class_dependency(option_selector, is_option_selected, dependent_class_config)

    def configure_class(self, options: Dict) -> Type:
        """
        Build a class using the selected configuration options, and then configure any dependent classes recursively.

        :param options: The configuration options.
        :return: The built class.
        """
        self.__setup_class_configuration(options)
        self.__prepare_class_dependencies()
        self.__parent_class_builder.configure_parent_classes()
        self.__component_class_builder.inject_components_before_or_after_methods()
        return type(
            self.__base_class.__name__,
            self.__parent_class_builder.parent_classes_configured,
            self.__component_class_builder.patched_methods
        )

    def build_configured_class(self, options: Dict) -> Type:
        """
        Build a class based on the options selected from the class configuration.

        :param options: The selected options.
        :return: The built class.
        """
        self.__config_manager.transform_options(options)
        return self.configure_class(options)

    def inject_components_into_method(self, obj: object, method: str, *args, **kwargs):
        """
        Inject components into a method of the given object based on the selected configuration.

        :param obj: The object on which the method is invoked.
        :param method: The method name.
        :param args: Positional arguments used to initialize the component class.
        :param kwargs: Keyword arguments used to initialize the component class.
        """
        self.__component_class_builder.explicitly_inject_components(obj, method, *args, **kwargs)
