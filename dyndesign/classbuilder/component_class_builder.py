from collections import defaultdict
from enum import IntEnum, auto
from typing import Any, Callable, Dict, List, Set, Type, Union

from .class_configuration_manager import ClassConfigurationManager
from .class_builder_config import ClassConfig
import dyndesign.exceptions as exc
from dyndesign.utils.misc import tuplefy
from dyndesign.dyninherit.dyninherit_base import safesuper
from dyndesign.utils.inspector import is_invoking_method_in_one_line, is_method_not_defined_in_class
from dyndesign.utils.signature import call_obj_with_adapted_args


class InjectionPosition(IntEnum):
    """Possible locations within the method's body where a component can be injected."""
    BEFORE = auto()
    MIDDLE = auto()
    AFTER = auto()


class ComponentClassBuilder:
    """ComponentClassBuilder is responsible for injecting component classes into a base class."""

    __COMPONENTS_APPLIED: Set = set()
    __EXPLICIT_METHOD_INJECTION: Dict = {}

    def __init__(self, base_class: Type, config_manager: ClassConfigurationManager,
                 configure_dependent_class_callback: Callable):
        """
        Initialize the ComponentClassBuilder instance.

        :param base_class: The base class to which components will be applied.
        :param config_manager: An instance of ClassConfigurationManager for loading configuration.
        :param configure_dependent_class_callback: A callback invoked to recursively configure the component classes.
        """
        self.__COMPONENTS_APPLIED = set()
        self.__base_class = base_class
        self.__config_manager = config_manager
        self.__configure_dependent_class = configure_dependent_class_callback
        self.__methods_to_patch: defaultdict = defaultdict(list)
        self.patched_methods: Dict = {}

    def __init_component(self, obj: object, component_conf: ClassConfig, *args, **kwargs) -> Union[Callable, None]:
        """
        Create a component instance by modifying the arguments of the injection method that are passed to the
        component's __init__ method, based on the given configuration. The component class is also configured so that
        all its potential dependent classes are recursively configured.

        :param obj: The object to which the component will be added.
        :param component_conf: The configuration of the component to be instantiated.
        :param args: Positional arguments to be passed to `__init__`.
        :param kwargs: Keyword arguments to be passed to `__init__`.
        :return: The component instance if the component is instantiated, None otherwise.
        """
        add_args = []
        add_kwargs = {}
        if component_conf.init_args_keep_first:
            args = args[0:component_conf.init_args_keep_first]
        if component_conf.init_args_from_self:
            for arg_name in tuplefy(component_conf.init_args_from_self):
                if hasattr(obj, arg_name):
                    add_args.append(getattr(obj, arg_name))
        if component_conf.init_kwargs_from_self:
            for kwarg_key, kwarg_name in component_conf.init_kwargs_from_self.items():
                if hasattr(obj, kwarg_name):
                    add_kwargs[kwarg_key] = getattr(obj, kwarg_name)
        component_class = (
            component_conf.component_class if component_conf.is_option_selected
            else self.__config_manager.get_default_class(component_conf)
        )
        return call_obj_with_adapted_args(
            self.__configure_dependent_class(component_class),
            None,
            *args, *add_args,
            strict_missing_args=bool(component_conf.strict_missing_args),
            **add_kwargs, **kwargs
        )

    def __is_the_right_injection_position(self, component_conf: ClassConfig, position: InjectionPosition) -> bool:
        """
        Determine if the component must be injected in the given position based on the configuration or not.

        :param component_conf: The component configuration.
        :param position: The injection position.
        :return: True if the injection is in the right position, False otherwise.
        """
        return (
            position == InjectionPosition.MIDDLE
            or (
                (position == InjectionPosition.BEFORE)
                ^ bool(self.__config_manager.get_global_setting(component_conf, 'add_components_after_method'))
            )
        )

    def __is_component_to_inject(self, component_conf: ClassConfig, position: InjectionPosition, method: str) -> bool:
        """
        Check whether the component must be injected or not.

        :param component_conf: The component configuration.
        :param position: The injection position.
        :param method: The method name.
        :return: True if the component must be injected, False otherwise.
        """
        return bool(
            self.__is_the_right_injection_position(component_conf, position)
            and component_conf.injection_method and method == component_conf.injection_method
            and (component_conf.component_class, method, component_conf.component_attr) not in self.__COMPONENTS_APPLIED
        )

    def __add_selector_components(self, selectors: List[str], obj: object, method: str, *args,
                                  position: InjectionPosition, **kwargs):
        """
        Add selector-specified components to the object based on configuration.

        :param selectors: The list of component selectors.
        :param obj: The object to which components will be added.
        :param method: The method to which the components are being added.
        :param args: Positional arguments used to initialize the component classes.
        :param position: The injection position.
        :param kwargs: Keyword arguments used to initialize the component classes.
        """
        for selector in selectors:
            for component_conf in tuplefy(self.__config_manager.class_conf[selector]):
                if (
                        self.__is_component_to_inject(component_conf, position, method)
                        and (component_instance := self.__init_component(obj, component_conf, *args, **kwargs))
                ):
                    setattr(obj, component_conf.component_attr, component_instance)
                    self.__COMPONENTS_APPLIED.add(
                        (component_conf.component_class, method, component_conf.component_attr)
                    )

    def __validate_component_configuration(self, class_config: ClassConfig):
        """
        Validate the class component configuration.

        :param class_config: The class component configuration to be validated.
        """
        if not class_config.component_attr:
            raise exc.ClassConfigMissingComponentAttr(
                "ClassConfig configurator must include the 'component_attr' field if the 'component_class' field is "
                "present"
            )
        if not hasattr(self.__base_class, str(class_config.injection_method)):
            raise exc.ClassConfigMissingComponentInjectionMethod(
                "The method specified in the 'injection_method' field does not exist in the base class"
            )

    def __invoke_injection_method(self, method: str, obj: object, *args, **kwargs) -> Any:
        """
        Invoke the injection method with adapted arguments. The arguments of the injection method may need to be
        modified to include additional or different arguments that are required by the component's __init__ constructor.

        :param method: The method name.
        :param obj: The object on which the method is invoked.
        :param args: Positional arguments used to initialize the component class and to pass to the injection method.
        :param kwargs: Keyword arguments used to initialize the component class and to pass to the injection method.
        :return: The result of the method invocation.
        """
        injection_method = getattr(self.__base_class, method)
        if injection_method:
            if is_method_not_defined_in_class(injection_method):
                # If the class inherits from a parent class, call the injection method from the parent class.
                if len(obj.__class__.__bases__) > 1:
                    injection_method = safesuper(obj.__class__.__base__, obj).__init__  # type: ignore
                    # In this case, the method needs to be called without passing `obj` as first argument.
                    obj = None
                else:
                    return None
            return call_obj_with_adapted_args(injection_method, obj, *args, strict_missing_args=True, **kwargs)
        return None

    def __has_components_explicitly_injected(self, selectors: List[str], method: str) -> bool:
        """
        If a method has a call to the component injector, record it to be processed in `explicitly_inject_components`.

        :param selectors: The list of component selectors.
        :param method: The method name.
        :return: True if the method has a call to the component injector, False otherwise.
        """
        method_instance = getattr(self.__base_class, method)
        if is_invoking_method_in_one_line(method_instance, "dynconfig.inject_components"):
            self.__EXPLICIT_METHOD_INJECTION[method] = selectors
            self.patched_methods[method] = method_instance
            return True
        return False

    def __patch_methods(self, selectors: List[str], method: str) -> None:
        """
        Patch a method by injecting components before or after its execution.

        :param selectors: The list of component selectors.
        :param method: The method name.
        """
        if self.__has_components_explicitly_injected(selectors, method):
            return

        def patched_method(obj: object, *args, **kwargs) -> Any:
            """
            This method is responsible for adding injected components to a method. It injects the components before
            or after invoking the original method and handles the adaptation of arguments.

            :param obj: The object on which the method is invoked.
            :param args: Positional arguments used to initialize the component class and to pass to the injection
                         method.
            :param kwargs: Keyword arguments used to initialize the component class and to pass to the injection method.
            :return: The result of the method invocation.
            """
            self.__add_selector_components(selectors, obj, method, *args, position=InjectionPosition.BEFORE, **kwargs)
            returned_value = self.__invoke_injection_method(method, obj, *args, **kwargs)
            self.__add_selector_components(selectors, obj, method, *args, position=InjectionPosition.AFTER, **kwargs)
            return returned_value

        self.patched_methods[method] = patched_method

    def select_component_class(self, option_selector: List[str], class_config: ClassConfig):
        """
        Select the component classes to be injected based on the configuration.

        :param option_selector: The configuration option selector.
        :param class_config: The configuration of the component class.
        """
        self.__config_manager.set_default_class_config(class_config, self.__config_manager.global_conf)
        self.__validate_component_configuration(class_config)
        self.__methods_to_patch[class_config.injection_method].append(option_selector)

    def inject_components_before_or_after_methods(self):
        """Inject component classes before or after corresponding methods based on the configuration."""
        for method, selectors in self.__methods_to_patch.items():
            self.__patch_methods(selectors, method)

    def explicitly_inject_components(self, obj: object, method: str, *args, **kwargs):
        """
        Inject components from an explicit injection point within a method based on the configuration, as opposed to
        implicitly injecting them either before or after the method.

        :param obj: The object on which the method is invoked.
        :param method: The method name.
        :param args: Positional arguments used to initialize the component class.
        :param kwargs: Keyword arguments used to initialize the component class.
        """
        selectors = self.__EXPLICIT_METHOD_INJECTION[method]
        self.__add_selector_components(selectors, obj, method, *args, position=InjectionPosition.MIDDLE, **kwargs)
