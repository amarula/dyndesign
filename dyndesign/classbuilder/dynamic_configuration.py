from collections import defaultdict
from types import FunctionType, SimpleNamespace
from typing import Any, Dict, Type, Optional

from .exposed_class_config import ClassConfig
from .class_builder import ClassBuilder
from .class_configuration_manager import ClassConfigurationManager, ClassConfigType, DependencyKeyType, MethodConfig
from .class_storage import ClassStorage
from .settings import CLASS_BUILDER_DEFAULT_CONFIG
import dyndesign.exceptions as exc
from dyndesign.utils.misc import get_dot_basename, class_to_dict
from dyndesign.utils.inspector import back_frame, get_class_name, get_instance_class_name

__all__ = ["buildclass", "dynconfig"]


class DynamicConfiguration:
    """DynamicConfiguration, also aliased as `dynconfig`, manages the Dynamic Class Configuration."""

    __CLASS_GLOBAL_CONFIG: Dict = {}
    __CLASS_OPTION_MAP: Dict = {}
    __METHOD_CONFIG_MAP: Dict = defaultdict(list)
    __ASSIGNED_CLASS_CONFIGS: Dict = defaultdict(dict)

    SWITCH_DEFAULT = ClassConfigurationManager.SWITCH_DEFAULT

    def __init__(self, *class_configs: ClassConfigType, **global_config):
        """
        Initialize the DynamicConfiguration instance.

        :param class_configs: One or more class configurations of potential dependencies.
        :param global_config: The global configuration settings.
        """
        config = {**CLASS_BUILDER_DEFAULT_CONFIG, **self.__CLASS_GLOBAL_CONFIG, **global_config}
        self.__global_config = SimpleNamespace(**config)
        self.__class_configs = class_configs or ({},)

    def __call__(self, obj: Any) -> Any:
        """
        When `dynconfig` is used as a class decorator, assign the configuration to the class.
        When it is used as a method decorator, assign the component injection configuration to the method.

        :param obj: The decorated object.
        :return: The decorated object.
        """
        if isinstance(obj, FunctionType):
            class_name = get_dot_basename(obj.__qualname__)
            self.__METHOD_CONFIG_MAP[class_name].append(MethodConfig(
                obj.__name__,
                self.__class_configs[ClassConfigurationManager.DEFAULT_UNIT_ID],
            ))
        else:
            self.__config_manager = ClassConfigurationManager(
                self.__global_config,
                self.__class_configs,
                self.__METHOD_CONFIG_MAP.get(obj.__name__),
                self.__ASSIGNED_CLASS_CONFIGS,
            )
            ClassStorage.config_map[obj] = ClassBuilder(obj, self.__config_manager)
        return obj

    @classmethod
    def __process_options(cls, options: Any = None, kw_options: Optional[Dict] = None) -> Dict:
        """
        Process the options for building the new class. If the `options` parameter is not a dictionary, convert it into
        one. If any keyword argument is passed, merge it into the options.

        :param options: Options passed as positional argument for building the new class.
        :param kw_options: Options passed as keyword arguments for building the new class.
        :return: The processed options.
        """
        if options is None:
            if kw_options is None:
                raise exc.BuildConfigWithoutOptions(
                    'At least one Building Option is required by "buildconfig"'
                )
            options = {}
        if not isinstance(options, dict):
            options = class_to_dict(options)
        options.update(kw_options or {})
        return options

    @classmethod
    def set_global(cls, **kwargs):
        """
        Set global configuration options passed as arguments.

        :param kwargs: Global configuration options.
        """
        cls.__CLASS_GLOBAL_CONFIG.update(kwargs)

    @classmethod
    def set_configuration(cls, option: DependencyKeyType, class_config: ClassConfig):
        """
        Assign a class configuration to an option from within a configurator class.

        :param option: The option to be set.
        :param class_config: The class configuration to be assigned to the option.
        """
        try:
            cls.__ASSIGNED_CLASS_CONFIGS[get_class_name(back_frame())][option] = class_config
        except KeyError:
            raise exc.BuildConfigWithoutOptions(
                'The "dynconfig.set_configuration" method must be used from within a configuration class'
            )

    @classmethod
    def build_class(cls, base_class: Type, options: Any = None, **kw_options) -> Type:
        """
        Build a new class based on a base class and the options selected from the class configuration.

        :param base_class: The base class to build upon.
        :param options: Options passed as first positional argument for building the new class.
        :param kw_options: Options passed as keyword arguments for building the new class.
        :return: The newly built class.
        """
        options = cls.__process_options(options, kw_options)
        cls.__CLASS_OPTION_MAP[base_class.__name__] = options
        class_built = ClassStorage.config_map[base_class].build_configured_class(options)
        ClassStorage.classes_built[class_built] = base_class
        return class_built

    @classmethod
    def buildcomponent(cls, base_class: Type) -> Type:
        """
        Build a new class within a containing built class based on the options selected for the containing class.

        :param base_class: The base class to build upon.
        :return: The built class if the method is called within a built class, the base class otherwise.
        """
        try:
            options = cls.__CLASS_OPTION_MAP[get_instance_class_name(back_frame())]
        except KeyError:
            return base_class
        return cls.build_class(base_class, options)

    @classmethod
    def inject_components(cls, *args, **kwargs):
        """
        Explicitly inject components into a method based on the configuration.

        :param args: Positional arguments used to initialize the component class.
        :param kwargs: Keyword arguments used to initialize the component class.
        """
        frame = back_frame()
        method = frame.f_code.co_name
        obj = frame.f_locals['self']
        base_class = ClassStorage.classes_built[obj.__class__]
        ClassStorage.config_map[base_class].inject_components_into_method(obj, method, *args, **kwargs)


dynconfig = DynamicConfiguration
buildclass = DynamicConfiguration.build_class
